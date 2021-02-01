from SQLighter import SQLighter
from config import DATABASE_NAME


def test_rows(test_name):
    return sql.get_all_table_rows(test_name)


sql = SQLighter(DATABASE_NAME)
testNames = sql.get_all_table_name()
sql_data = {}

for test in testNames:
    NameAndGenre = test.split('_')
    genre_test = NameAndGenre[-1].replace('$', ' ')
    name_test = ' '.join(NameAndGenre[0: len(NameAndGenre) - 1])
    for row in test_rows(test):
        if sql_data.get(genre_test) is None:
            sql_data[genre_test] = {
                name_test: [{'id': row[0], 'question': row[1], 'correct_answer': row[2], 'wrong_answers': row[3],
                             'advice': row[4]}]}
        else:
            sql_data[genre_test][name_test] = sql_data[genre_test].get(name_test, []) + [
                {'id': row[0], 'question': row[1], 'correct_answer': row[2], 'wrong_answers': row[3], 'advice': row[4]}]
# print(sql_data['Спорт']['Физкультура 1'][0]['id'])
sql.close()
