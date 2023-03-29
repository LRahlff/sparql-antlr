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
	start_time = time.time()
	f = open('../python-addon/connection_properties.json')
	data = json.load(f)
	database = data['conn_details'][0]['database']
	user = data['conn_details'][0]['user']
	password = data['conn_details'][0]['password']
	host = data['conn_details'][0]['host']
	port = data['conn_details'][0]['port']

	f.close()
	if len(sys.argv) < 2:
		print("taking file as query")
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
	# tree = myTree.forward
	# for subj in tree:
	# 	print(subj)
	# 	for pred in tree[subj]:
	# 		print('    ' + str(pred))
	# 		for obj in tree[subj][pred]:
	# 			print('        ' + str(obj))
	#
	# print('----------------------------------')
	#
	#
	# revtree = myTree.reverse
	# for subj in revtree:
	# 	print(subj)
	# 	for pred in revtree[subj]:
	# 		print('    ' + str(pred))
	# 		for obj in revtree[subj][pred]:
	# 			print('        ' + str(obj))
	#
	# print('----------------------------------')

	myTree.traverseVars()


	calc_time_stamp = time.time()

	conn = psycopg2.connect(
		database=database,
		user=user,
		password=password,
		host=host,
		port=port
	)

	cursor = conn.cursor()

	cursor.execute("DELETE FROM new_param_id;")
	cursor.execute("DELETE FROM new_mat_sample_id;")
	cursor.execute("DELETE FROM new_mat_samples;")
	cursor.execute("DELETE FROM new_value;")

	sql_insert_value = lambda table, val_id, obj : "INSERT INTO " + table +\
											 " SELECT DISTINCT '" + val_id + "' AS new_val_id, " \
																"p.param_id AS param_id " \
												"FROM param p " \
												"WHERE param_id LIKE '" + obj + "';"
	sql_insert_material = lambda table, val_id, obj : "INSERT INTO " + table +\
											 " SELECT DISTINCT '" + val_id + "' AS new_val_id, " \
																"m.mat_sample_id AS mat_sample_id " \
												"FROM (SELECT sample_id AS mat_sample_id FROM sample " \
														"UNION SELECT mat_id AS mat_sample_id FROM material " \
														"UNION SELECT mat_sample_id AS mat_sample_id FROM new_mat_samples " \
														") m " \
												"WHERE mat_sample_id LIKE '" + obj + "';"

	new_mat = myTree.get_new_materials()

	# Todo : better way, maybe with lamda function
	for m in new_mat:
		cursor.execute("INSERT INTO new_mat_samples VALUES ('" + m + "') ;")
	conn.commit()

	new_values = myTree.get_new_params()

	tree = myTree.forward
	rev_tree = myTree.reverse
	for new_value in new_values:
		if tree.get(new_value) is not None:
			if tree[new_value].get(A_NODE) is not None:
				for obj in tree[new_value][A_NODE]:
					if obj.type == 'string':
						cursor.execute(sql_insert_value('new_param_id', new_value.name, obj.name))
					if obj.type == 'konzept':
						if koncept_translation.get(obj.name) is not None:
							cursor.execute(sql_insert_value('new_param_id', new_value.name, koncept_translation[obj.name]))
						else:
							cursor.execute(sql_insert_value('new_param_id', new_value.name, obj.name))

			if tree[new_value].get(HAT_WERT_NODE) is not None:
				for obj in tree[new_value][HAT_WERT_NODE]:
					if obj.type == 'numeric':
						cursor.execute("INSERT INTO new_value VALUES ('" + new_value.name + "', " + obj.name + ") ;")

		if rev_tree.get(new_value) is not None:
			if rev_tree[new_value].get(HAT_PARAMETER_NODE) is not None:
				for subrev in rev_tree[new_value][HAT_PARAMETER_NODE]:
					if tree.get(subrev) is not None:
						if tree[subrev].get(HAT_NAME_NODE) is not None:
							for obj2 in tree[subrev][HAT_NAME_NODE]:
								if obj2.type == 'string' or obj2.type == 'konzept':
									cursor.execute(sql_insert_material('new_mat_sample_id', new_value.name, obj2.name))
	conn.commit()

	cursor.execute("REFRESH MATERIALIZED VIEW new_concr_param")
	cursor.execute("REFRESH MATERIALIZED VIEW new_concr_param_view")
	cursor.execute("REFRESH MATERIALIZED VIEW concr_parameter")
	cursor.execute("REFRESH MATERIALIZED VIEW concr_parameter_new_only")
	cursor.execute("REFRESH MATERIALIZED VIEW concr_curve_params")
	cursor.execute("REFRESH MATERIALIZED VIEW concr_curve")
	cursor.execute("REFRESH MATERIALIZED VIEW concr_curve_params_temp")
	cursor.execute("REFRESH MATERIALIZED VIEW names")

	conn.commit()
	# Closing the connection
	conn.close()

	end_time = time.time()
	print('calc_time: ' + str(calc_time_stamp - start_time) + ' , refresh_time: ' + str(end_time - calc_time_stamp))
	print(' Ende')
