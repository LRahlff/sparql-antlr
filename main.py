import sys
from antlr4 import *

from MyNode import MyNode
from MyRelationTree import MyRelationTree
from MyWalkListener import MyWalkListener
from gen.SparqlLexer import SparqlLexer
from gen.SparqlParser import SparqlParser

# https://github.com/antlr/grammars-v4/blob/master/sparql/Sparql.g4
# attention: grammar now changed a little

if __name__ == '__main__':

	sqlrequest = ""
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

	sql_insert_new_material = lambda materials: "INSERT INTO new_mat_samples " \
													"SELECT DISTINCT new_mat.mat " \
													"FROM (VALUES " + materials + ") AS new_mat (mat) " \
														"LEFT OUTER JOIN  " \
														"(	SELECT sample_id AS mat_sample_id " \
															"FROM sample " \
															"UNION SELECT mat_id AS mat_sample_id FROM material " \
														") m " \
															"ON m.mat_sample_id = new_mat.mat " \
														"WHERE m.mat_sample_id IS NULL ; "

	sql_insert_param_id = lambda new_params: "INSERT INTO new_param_id " +\
												"SELECT DISTINCT " +\
												"newval.new_val_id, " +\
												"p.param_id " +\
												"FROM  " +\
													"(VALUES " + new_params + ") AS newval (new_val_id, param_id) " +\
													"LEFT OUTER JOIN " +\
													"param p " +\
													"ON p.param_id = newval.param_id " +\
												"WHERE p.param_id IS NOT NULL"

	sql_insert_value = lambda new_values: "INSERT INTO new_value " +\
												"SELECT DISTINCT " +\
												"valid.new_val_id, " +\
												"newval.value " +\
												"FROM  " +\
													"(VALUES " + new_values + ") AS newval (new_val_id, value) " +\
													"LEFT OUTER JOIN " +\
													"new_param_id valid " +\
													"ON valid.new_val_id = newval.new_val_id " +\
												"WHERE valid.new_val_id IS NOT NULL"

	sql_insert_material = lambda new_material: "INSERT INTO new_mat_sample_id " +\
												"SELECT DISTINCT " +\
												"valid.new_val_id, " +\
												"m.mat_sample_id " +\
												"FROM  " +\
													"(VALUES " + new_material + ") AS newmat (new_val_id, material) " +\
													"LEFT OUTER JOIN  " \
													"(SELECT sample_id AS mat_sample_id FROM sample " \
														"UNION SELECT mat_id AS mat_sample_id FROM material " \
														"UNION SELECT mat_sample_id AS mat_sample_id FROM new_mat_samples " \
													") m " \
													"ON m.mat_sample_id = newmat.material " +\
													"LEFT OUTER JOIN " +\
														"new_param_id valid " +\
													"ON valid.new_val_id = newmat.new_val_id " +\
												"WHERE m.mat_sample_id IS NOT NULL AND valid.new_val_id IS NOT NULL"

	new_mat = myTree.get_new_materials()

	# Todo : better way, maybe with lamda function
	if len(new_mat)>0:
		materials = "('" + "'), ('".join(new_mat) + "')"
		sqlrequest += sql_insert_new_material(materials)

	new_values = myTree.get_new_params()

	tree = myTree.forward
	rev_tree = myTree.reverse
	params = []
	values = []
	material = []
	for new_value in new_values:
		if tree.get(new_value) is not None:
			if tree[new_value].get(A_NODE) is not None:
				for obj in tree[new_value][A_NODE]:
					if obj.type == 'string':
						params.append("('" + new_value.name + "', '" + obj.name + "')")
					if obj.type == 'konzept':
						if koncept_translation.get(obj.name) is not None:
							params.append("('" + new_value.name + "', '" + koncept_translation[obj.name] + "')")
						else:
							params.append("('" + new_value.name + "', '" + obj.name + "')")

			if tree[new_value].get(HAT_WERT_NODE) is not None:
				for obj in tree[new_value][HAT_WERT_NODE]:
					if obj.type == 'numeric':
						values.append("('" + new_value.name + "', " + obj.name + ")")

		if rev_tree.get(new_value) is not None:
			if rev_tree[new_value].get(HAT_PARAMETER_NODE) is not None:
				for subrev in rev_tree[new_value][HAT_PARAMETER_NODE]:
					if tree.get(subrev) is not None:
						if tree[subrev].get(HAT_NAME_NODE) is not None:
							for obj2 in tree[subrev][HAT_NAME_NODE]:
								if obj2.type == 'string' or obj2.type == 'konzept':
									material.append("('" + new_value.name + "', '" + obj2.name + "')")
	sqlrequest += sql_insert_param_id(", ".join(params)) + " ; "
	sqlrequest += sql_insert_value(", ".join(values)) + " ; "
	sqlrequest += sql_insert_material(", ".join(material)) + " ; "
	print(sqlrequest)
