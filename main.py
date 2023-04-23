import json
import re
import sys

import time

from antlr4 import *

from MyNode import MyNode
from MyRelationTree import MyRelationTree
from MyWalkListener import MyWalkListener
from gen.SparqlLexer import SparqlLexer
from gen.SparqlParser import SparqlParser

# importing psycopg2 module
import psycopg2




# https://github.com/antlr/grammars-v4/blob/master/sparql/Sparql.g4
# attention: grammar now changed a little

if __name__ == '__main__':

	sqlrequest = ""
	start_time = time.time()
	if len(sys.argv) < 2:
		with open('query_new.txt', 'r') as fr:
			query = fr.read()
	else:
		query = sys.argv[1]

	sparql_lexer = SparqlLexer(InputStream(query))
	sparql_tokens = CommonTokenStream(sparql_lexer)
	sparql_parser = SparqlParser(sparql_tokens)
	start = sparql_parser.query()

	walker = ParseTreeWalker()

	myTree = MyRelationTree()

	listener = MyWalkListener(myTree)

	walker.walk(listener, start)

	A_NODE = MyNode('verb', 'a')
	HAT_WERT_NODE = MyNode('konzept', 'hat_Wert')
	HAT_PARAMETER_NODE = MyNode('konzept', 'hat_Parameter')
	HAT_NAME_NODE = MyNode('konzept', 'hat_Name')

	koncept_translation = {
		'piezoelektrisches_Moment': 'piezoelektrische_Moment'
	}

	myTree.traverseVars()


	calc_time_stamp = time.time()

	# cursor.execute("DELETE FROM new_param_id;")
	# cursor.execute("DELETE FROM new_mat_sample_id;")
	# cursor.execute("DELETE FROM new_mat_samples;")
	# cursor.execute("DELETE FROM new_value;")

	sql_insert_value = lambda table, val_id, value : "INSERT INTO " + table +\
											 " SELECT DISTINCT '" + val_id + "' AS new_val_id, " \
																"p.param_id AS param_id " \
												"FROM param p " \
												"WHERE param_id LIKE '" + value + "'; "
	sql_insert_material = lambda table, val_id, material: "INSERT INTO " + table +\
											 " SELECT DISTINCT '" + val_id + "' AS new_val_id, " \
																"m.mat_sample_id AS mat_sample_id " \
												"FROM (SELECT sample_id AS mat_sample_id FROM sample " \
														"UNION SELECT mat_id AS mat_sample_id FROM material " \
														"UNION SELECT mat_sample_id AS mat_sample_id FROM new_mat_samples " \
														") m " \
												"WHERE mat_sample_id LIKE '" + material + "'; "
	sql_insert_new_material = lambda table, new_material: "INSERT INTO " + table +\
											 " SELECT DISTINCT new_mat.mat FROM " \
												"(VALUES ('" + new_material+ "')) AS new_mat (mat) " \
												"LEFT OUTER JOIN  " \
												"(	SELECT sample_id AS mat_sample_id " \
													"FROM sample " \
													"UNION SELECT mat_id AS mat_sample_id FROM material " \
												") m " \
												"ON m.mat_sample_id = new_mat.mat " \
												"WHERE m.mat_sample_id IS NULL ; "

	new_mat = myTree.get_new_materials()

	# Todo : better way, maybe with lamda function
	for m in new_mat:
		sqlrequest += sql_insert_new_material("new_mat_samples", m)

	new_values = myTree.get_new_params()

	tree = myTree.forward
	rev_tree = myTree.reverse
	for new_value in new_values:
		if tree.get(new_value) is not None:
			if tree[new_value].get(A_NODE) is not None:
				for obj in tree[new_value][A_NODE]:
					if obj.type == 'string':
						sqlrequest += sql_insert_value('new_param_id', new_value.name, obj.name)
					if obj.type == 'konzept':
						if koncept_translation.get(obj.name) is not None:
							sqlrequest += sql_insert_value('new_param_id', new_value.name, koncept_translation[obj.name])
						else:
							sqlrequest += sql_insert_value('new_param_id', new_value.name, obj.name)

			if tree[new_value].get(HAT_WERT_NODE) is not None:
				for obj in tree[new_value][HAT_WERT_NODE]:
					if obj.type == 'numeric':
						sqlrequest += "INSERT INTO new_value VALUES ('" + new_value.name + "', " + obj.name + ") ; "

		if rev_tree.get(new_value) is not None:
			if rev_tree[new_value].get(HAT_PARAMETER_NODE) is not None:
				for subrev in rev_tree[new_value][HAT_PARAMETER_NODE]:
					if tree.get(subrev) is not None:
						if tree[subrev].get(HAT_NAME_NODE) is not None:
							for obj2 in tree[subrev][HAT_NAME_NODE]:
								if obj2.type == 'string' or obj2.type == 'konzept':
									sqlrequest += sql_insert_material('new_mat_sample_id', new_value.name, obj2.name)


	end_time = time.time()
	print('Ende: calc_time: ' + str(calc_time_stamp - start_time))
	print(sqlrequest)
