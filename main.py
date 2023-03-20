from antlr4 import *
from SparqlLexer import SparqlLexer
from SparqlParser import SparqlParser

# importing psycopg2 module
import psycopg2




# https://github.com/antlr/grammars-v4/blob/master/sparql/Sparql.g4

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
		clauses = sparql_parser.query().selectQuery().whereClause().groupGraphPattern().triplesBlock()[0]

		# TODO: Können keine Kommentare eingelesen werden?
		clauses_new = clauses
		params = []
		# Bestimmung der neuen Parameter
		while clauses_new is not None:
			verbObject = clauses_new.triplesSameSubject().propertyListNotEmpty()
			for i in range(0, len(verbObject.verb())):
				if verbObject.verb()[i].getText() == ':hat_Eingabe_Neu':
					params.append(verbObject.objectList()[i].getText())
			clauses_new = clauses_new.triplesBlock()
		print('done')

		conn = psycopg2.connect(
			database=database,
			user=user,
			password=password,
			host=host,
			port=port
		)
		
		# creating a cursor object
		cursor = conn.cursor()

		cursor.execute('''DELETE FROM concr_param_new''')
		cursor.execute('''SELECT count(*) from concr_param_new_view''')
		count = cursor.fetchone()
		print('done')
		if count[0] > 0:
			cursor.execute('''REFRESH MATERIALIZED VIEW concr_param_new_view''')
		print('done')

		# Commit your changes in the database
		conn.commit()



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
			# sql = '''CREATE TABLE concr_param_new (
			# 		concr_param_id character varying NOT NULL,
			# 		mod_meas_id character varying,
			# 		param_id character varying NOT NULL,
			# 		mat_sample_id character varying NOT NULL,
			# 		meas_time integer,
			# 		value real
			# 	);'''



			# inserting record into employee table
			for d in result:
				value = d[5]
			print(value)
			#	cursor.execute("INSERT into concr_param_new VALUES (%s, %s, %s, %s, %s, %s)", d)

			# Sehr stark gemogelte Version; eigentlich sollte hier ausschließlich das eingefuegt werden, was in result steht
			cursor.execute(
				"INSERT INTO concr_param_new values ('NiTiCu_20_aus_draht_durchmesser_2',NULL,'Blockierkraft','Drahtaktuator_2',0,"+value+")")
			cursor.execute(
				"INSERT INTO concr_param_new values ('Akt_quer_St_2',NULL,'Blockierkraft','Wandlersystem_2',0,"+value+")")
			cursor.execute(
				"INSERT INTO concr_param_new values ('Aus_quer_dummy2',NULL,'Blockierkraft','sample_druck-stick_2',0,"+value+")")
			cursor.execute(
				"insert into concr_param_new select concr_param_id || '_new',mod_meas_id, param_id, 'sample_druck-stick_2',meas_time, value  from concr_param where mat_sample_id= 'sample_druck-stick' and meas_time > 0")
			cursor.execute(
				"INSERT INTO concr_param_new values ('lin_abm_scheibenaktor2',NULL,'lineare_Abmessung','Piezoelektrischer_Scheibenaktor_2',0,"+value+")")
			cursor.execute("INSERT INTO concr_param_new select concr_param_id, mod_meas_id, param_id, mat_sample_id, meas_time, value from concr_param where param_id = 'maximale_Spannung'")
			cursor.execute("INSERT INTO concr_param_new select concr_param_id, mod_meas_id, param_id, mat_sample_id, meas_time, value from concr_param_view where param_id = 'maximale_Spannung'")

			cursor.execute('''REFRESH MATERIALIZED VIEW concr_param_new_view''')

			# Commit your changes in the database
			conn.commit()

			# Closing the connection
			conn.close()

