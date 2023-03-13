import json
import re
import sys

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
	f = open('connection_properties.json')
	data = json.load(f)
	database = data['conn_details'][0]['database']
	user = data['conn_details'][0]['user']
	password = data['conn_details'][0]['password']
	host = data['conn_details'][0]['host']
	port = data['conn_details'][0]['port']
	f.close()
	print("\\")
	print("#")
	print("\#")
	if len(sys.argv) < 2:
		print("not enough arguments")
		sys.exit()
	print(sys.argv[1])
	query = sys.argv[1]
	abc = re.sub("\\\#", " ", query)
	print(query)
	print(abc)
	testq = """PREFIX : <urn:absolute/prototyp#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?p ?vn ?nn  ?mat1 ?material1
WHERE {
    
}

# ?p1 :hat_Herkunft :Parameter_Neu -> Material

# cli sqltranslation für namen oder hardcoden

# Parameter bleibt bei Konzept
	"""
	sparql_lexer = SparqlLexer(InputStream(testq))
	sparql_tokens = CommonTokenStream(sparql_lexer)
	sparql_parser = SparqlParser(sparql_tokens)
	start = sparql_parser.query()

	walker = ParseTreeWalker()


	myTree = MyRelationTree()

	listener = MyWalkListener(myTree)

	walker.walk(listener, start)


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


	# print('----------------------------------')
	# tree = myTree.forward
	# for subj in tree:
	# 	print(subj)
	# 	for pred in tree[subj]:
	# 		print('    ' + str(pred))
	# 		for obj in tree[subj][pred]:
	# 			print('        ' + str(obj))



	print('finish')

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



	# cursor.execute("DROP TABLE IF EXISTS new_param_id;")
	# cursor.execute("CREATE TABLE new_param_id (new_val_id character varying, param_id character varying);")
	# cursor.execute("DROP TABLE IF EXISTS new_mat_sample_id;")
	# cursor.execute("CREATE TABLE new_mat_sample_id (new_val_id character varying, mat_sample_id character varying);")
	# cursor.execute("DROP TABLE IF EXISTS new_mat_samples;")
	# cursor.execute("CREATE TABLE new_mat_samples (mat_sample_id character varying);")
	# cursor.execute("DELETE FROM new_mat_samples;")
	# cursor.execute("DROP TABLE IF EXISTS new_value;")
	# cursor.execute("CREATE TABLE new_value (new_val_id character varying, value double precision);")


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
			node = MyNode('verb', 'a')
			if tree[new_value].get(node) is not None:
				for obj in tree[new_value][node]:
					if obj.type == 'string' or obj.type == 'konzept':
						cursor.execute(sql_insert_value('new_param_id', new_value.name, obj.name))

			node = MyNode('konzept', 'hat_Wert')
			if tree[new_value].get(node) is not None:
				for obj in tree[new_value][node]:
					if obj.type == 'numeric':
						cursor.execute("INSERT INTO new_value VALUES ('" + new_value.name + "', " + obj.name + ") ;")

		if rev_tree.get(new_value) is not None:
			node = MyNode('konzept', 'hat_Parameter')
			if rev_tree[new_value].get(node) is not None:
				for subrev in rev_tree[new_value][node]:
					if tree.get(subrev) is not None:
						node2 = MyNode('konzept', 'hat_Name')
						if tree[subrev].get(node2) is not None:
							for obj2 in tree[subrev][node2]:
								if obj2.type == 'string' or obj2.type == 'konzept':
									cursor.execute(sql_insert_material('new_mat_sample_id', new_value.name, obj2.name))
	conn.commit()

	# cursor.execute("""INSERT INTO new_concr_param
	# 					SELECT
	# 						values.new_val_id || '_' || COALESCE(params.param_id,'undefined_parameter') || '_' || COALESCE(mat_samples.mat_sample_id, 'undefined') || '_' || values.value AS concr_param_id,
	# 						'new_Val' AS mod_meas_id,
	# 						COALESCE(params.param_id,'undefined_parameter') AS param_id,
	# 						COALESCE(mat_samples.mat_sample_id, 'undefined') AS mat_sample_id,
	# 						0 AS meas_time,
	# 						values.value AS value
	# 					FROM new_value values
	# 						LEFT JOIN
	# 						new_mat_sample_id mat_samples
	# 							ON values.new_val_id = mat_samples.new_val_id
	# 						LEFT JOIN
	# 						new_param_id params
	# 							ON values.new_val_id = params.new_val_id;""")
	#
	# conn.commit()
	# print('done')

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

	print('Ende')
