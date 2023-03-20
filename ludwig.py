import json




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
	
	with open('query.txt', 'r') as fr:
		print('done')

		sparql_lexer = SparqlLexer(InputStream(fr.read()))
		sparql_tokens = CommonTokenStream(sparql_lexer)
		sparql_parser = SparqlParser(sparql_tokens)
		# TODO other grammar cases to do
		whCl = sparql_parser.query().selectQuery().whereClause()
		groupPatt = whCl.groupGraphPattern()
		# TODO if there is not triplesBlock?
		clauses = groupPatt.a


		# remember new values
		new_values = set()
		new_mat = set()
		# Graph bauen
		subj = {}
		reverseRel = {}

		if clauses != None:
			clauses_new = clauses
			while clauses_new is not None:
				# TODO other grammar cases to do
				verbObject = clauses_new.triplesSameSubject().propertyListNotEmpty()
				noun = clauses_new.triplesSameSubject().varOrTerm()
				# print(noun.getText())
				subjNow = noun.getText()
				if subj.get(subjNow) is None:
					subj[subjNow] = {}
				for i in range(0, len(verbObject.verb())):
					verbNow = verbObject.verb()[i].getText()
					objNow = verbObject.objectList()[i].getText()
					if objNow == ':Parameter_Neu' and verbNow == 'a':
						new_values.add(subjNow)
					elif objNow == ':Material_Neu' and verbNow == 'a':
						new_mat.add(subjNow)
					# elif objNow == ':Parameter_Neu' and verbNow == 'a':
					# 	new_values.add(subjNow)
					else:
						if subj[subjNow].get(verbNow) is None:
							subj[subjNow][verbNow] = set()
						(subj[subjNow].get(verbNow)).add(objNow)
					if reverseRel.get(objNow) is None:
						reverseRel[objNow] = {}
					if reverseRel[objNow].get(verbNow) is None:
						reverseRel[objNow][verbNow] = set()
					reverseRel[objNow][verbNow].add(subjNow)

				clauses_new = clauses_new.triplesBlock()



		filter = groupPatt.filter_()
		print(subj)

		# Fuege alle Filter direkt der Realtion zu
		for f in filter:
			andExpr = f.constraint().brackettedExpression().expression().conditionalOrExpression().conditionalAndExpression()
			for andE in andExpr:
				# print(andE.getText())
				for val in andE.valueLogical():
					# print(val.getText())
					relEx = val.relationalExpression()
					# print(relEx.l.getText())
					left = relEx.l.getText()
					if (relEx.m is not None):
						# print(relEx.r.getText())
						# print(relEx.m.text)
						if (relEx.m.text == '='):
							# if reverseRel.get(left) is not None:
							# 	test
							for relation in reverseRel[left]:
								for subjhere in reverseRel[left][relation]:
									if relEx.r.getText() == ':Parameter_Neu' and relation == 'a':
										new_values.add(subjhere)
									elif relEx.r.getText() == ':Material_Neu' and relation == 'a':
										new_mat.add(subjhere)
									else:
										# TODO Zwischen Variablen und Dings unterscheiden
										subj[subjhere][relation].add(relEx.r.getText())
										if left in subj[subjhere][relation]:
											subj[subjhere][relation].remove(left)

							pass
					if (relEx.n is not None):
						# print(relEx.n.text)
						if(relEx.n.text == 'IN'):
							if reverseRel.get(left) is not None:
								for relation in reverseRel[left]:
									for subjhere in reverseRel[left][relation]:
										for exp in relEx.expression():
											if exp.getText() == ':Parameter_Neu' and relation == 'a':
												new_values.add(subjhere)
											elif exp.getText() == ':Material_Neu' and relation == 'a':
												new_mat.add(subjhere)
											else:
												# TODO Zwischen Variablen und Dings unterscheiden
												subj[subjhere][relation].add(exp.getText())
										if left in subj[subjhere][relation]:
											subj[subjhere][relation].remove(left)
		print(subj)

		# print(reverseRel)
		# for rev in reverseRel:
		# 	print('' + rev + '' + str(reverseRel[rev]))
		conn = psycopg2.connect(
			database=database,
			user=user,
			password=password,
			host=host,
			port=port
		)


		# creating a cursor object
		cursor = conn.cursor()
		# cursor.execute("SELECT count(*) from concr_param_view")
		# count = cursor.fetchone()
		# print('done: ' + str(count))

		cursor.execute("DELETE FROM concr_param_new;")
		cursor.execute("DROP TABLE IF EXISTS new_param_id;")
		cursor.execute("CREATE TABLE new_param_id (new_val_id character varying, param_id character varying);")
		cursor.execute("DROP TABLE IF EXISTS new_mat_sample_id;")
		cursor.execute("CREATE TABLE new_mat_sample_id (new_val_id character varying, mat_sample_id character varying);")
		cursor.execute("DROP TABLE IF EXISTS new_mat_samples;")
		cursor.execute("CREATE TABLE new_mat_samples (mat_sample_id character varying);")
		cursor.execute("DROP TABLE IF EXISTS new_value;")
		cursor.execute("CREATE TABLE new_value (new_val_id character varying, value double precision);")


		sql_insert_value = lambda table, val_id, obj : "INSERT INTO " + table +\
												 " SELECT DISTINCT '" + val_id + "' AS new_val_id, " \
																	"p.param_id AS param_id " \
													"FROM param p " \
													"WHERE param_id LIKE '" + obj[1:] + "';"
		sql_insert_material = lambda table, val_id, obj : "INSERT INTO " + table +\
												 " SELECT DISTINCT '" + val_id + "' AS new_val_id, " \
																	"m.mat_sample_id AS mat_sample_id " \
													"FROM (SELECT sample_id AS mat_sample_id FROM sample " \
															"UNION SELECT mat_id AS mat_sample_id FROM material " \
															"UNION SELECT mat_sample_id AS mat_sample_id FROM new_mat_samples " \
															") m " \
													"WHERE mat_sample_id LIKE '" + obj[1:] + "';"
		print(new_mat)
		print(reverseRel)
		for newm in new_mat:
			for verb in subj[newm]:
				if verb == ':hat_Name':
					for obj in subj[newm][verb]:
						cursor.execute("INSERT INTO new_mat_samples VALUES ('" + obj[1:] + "') ;")
		for new_value in new_values:
			children = subj[new_value]
			for verb in children:
				if verb == 'a':
					for obj in children[verb]:
						# TODO Zwischen Variablen und Dings unterscheiden
						cursor.execute(sql_insert_value('new_param_id', new_value, obj))
				if verb == ':hat_Wert':
					for obj in children[verb]:
						# TODO Zwischen Variablen und Dings unterscheiden
						cursor.execute("INSERT INTO new_value VALUES ('" + new_value + "', " + obj[1:-1] + ") ;")
			for verb in reverseRel[new_value]:
				if verb == ':hat_Parameter':
					for noun in reverseRel[new_value][verb]:
						for verb2 in subj[noun]:
							if verb2 == ':hat_Name':
								for obj2 in subj[noun][verb2]:
									# cursor.execute("INSERT INTO new_mat_sample_id VALUES ('" + new_value + "', '" + obj2[1:] + "') ;")
									cursor.execute(sql_insert_material('new_mat_sample_id', new_value, obj2))




		cursor.execute("""INSERT INTO concr_param_new
							SELECT
								values.new_val_id || '_' || COALESCE(params.param_id,'undefined_parameter') || '_' || COALESCE(mat_samples.mat_sample_id, 'undefined') || '_' || values.value AS concr_param_id,
								'new_Val' AS mod_meas_id,
								COALESCE(params.param_id,'undefined_parameter') AS param_id,
								COALESCE(mat_samples.mat_sample_id, 'undefined') AS mat_sample_id,
								0 AS meas_time,
								values.value AS value
							FROM new_value values
								LEFT JOIN 
								new_mat_sample_id mat_samples
									ON values.new_val_id = mat_samples.new_val_id
								LEFT JOIN
								new_param_id params
									ON values.new_val_id = params.new_val_id;""")
		# WHERE COALESCE(mat_samples.new_val_id, params.new_val_id, values.new_val_id) ='""" + new_value + """'
		print('done')

		# Commit your changes in the database
		conn.commit()



		conn.commit()


		params = []

		if len(params) > 0:
			result = []
			# vernünftige ID festlegen
			for p in params:
				# 1. ID,
				# 2. mod_meas_id
				# 3. param_id
				# 4. mat_sample_id (einfuegen eines Dummys, ersetzen falls Info vorhanden)
				# 5. meas_time (erstmal 0)
				# 6. Wert
				# TODO: Matrixelemente fehlen noch
				result.append(['123'+p, 'NULL',None , 'unknown_material', 0, None])

			# Bestimmung der Werte der Parameter
			clauses_new = clauses
			while clauses_new is not None:
				noun = clauses_new.triplesSameSubject().varOrTerm()
				print('Test' + noun.getText())
				verbObject = clauses_new.triplesSameSubject().propertyListNotEmpty()
				for i in range(0, len(verbObject.verb())):
					if noun.getText() in params:

						index = params.index(noun.getText())
						if verbObject.verb()[i].getText() == 'a':
							result[index][2] = verbObject.objectList()[i].getText()[1:]
						if verbObject.verb()[i].getText() == ':hat_Wert':
							result[index][5] = verbObject.objectList()[i].getText().strip('\"')
						if verbObject.verb()[i].getText() == ':besteht_aus':
							# Material wird entweder durch Filter oder durch eine 'hat_Name'-Relation festgelegt
							# TODO: Behandlung fehlt noch
							pass
				clauses_new = clauses_new.triplesBlock()


			print(result)
			# Schreiben einer View, die die Einträge aus result enthält; Aufruf einer refresh_view-Funktion,
			# die nur notwendige Neuberechnungen durchführt, d.h., welche, die auf den neuen Werten basieren
			# establishing the connection



			# creating table
			# sql = "CREATE TABLE concr_param_new (
			# 		concr_param_id character varying NOT NULL,
			# 		mod_meas_id character varying,
			# 		param_id character varying NOT NULL,
			# 		mat_sample_id character varying NOT NULL,
			# 		meas_time integer,
			# 		value real
			# 	);"

			# Commit your changes in the database
			conn.commit()

			# Closing the connection
			conn.close()
