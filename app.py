from flask import Flask, abort, request, jsonify
from flask_cors import CORS
import sqlite3 as sl
from random import choice, randint
app = Flask(__name__)
cors = CORS(app)
lessons = {0: 12, 1: 26, 2: 21, 3: 16, 4: 23, 5: 21, 6: 20, 7: 12, 8: 28, 9: 10}
@app.route('/exercises/', methods = ['GET'])
def exercises():
    exes = []
    abc = request.args.get('lesson', '')
    for i in range(1, lessons[int(abc)]):
        exes.append(i)
    #number = choice(exes)
    number = choice([0, 2, 1])
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * from exercises')
    records = cursor.fetchall()
    result = {}
    for row in records:
        if (row[0].split('.')[-1] == str(number)) and (row[0].split('.')[0] == abc):
        #if row[0].split('.')[0] == str(abc):
            result = {'id': row[0], 'text': row[1], 'correct': row[2], 'image': row[3], 'score': row[-1]}
    return jsonify(result)
@app.route('/lent/', methods = ['GET'])
def lent():
    abc = request.args.get('number', '') 
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    result = {}
    cursor.execute('SELECT * from lent')
    records = cursor.fetchall()
    if len(records) - int(abc) <= 0:
        result = {'number': 0, 'autor': 'EasyPass', 'text': 'Ты посмотрел все публикации!', 'score': 'бесконечность'}
    else:
        for row in records:
            if len(records) - int(abc) == row[3]:
                cursor.execute('SELECT * FROM users')
                records1 = cursor.fetchall()
                for row1 in records1:
                    if str(row1[8]) == row[0]:
                        autor = row1[0]
                        score = row1[3]
                        avatar = row1[4]
                        id = row1[5]
                        result = {'number': row[3], 'autor': autor, 'text': row[1], 'score': score, 'avatar': avatar, 'file': row[2], 'id': id, 'likes': row[4]}
    return jsonify(result)
@app.route('/publicate', methods = ['POST'])
def publicate():
    new = request.json
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM lent')
    records = cursor.fetchall()
    cursor.execute('INSERT INTO lent (id, text, file, ip, likes) VALUES (?, ?, ?, ?, ?)', (new['hash'], new['text'], new['file'], len(records)+1, 0))
    con.commit()
    con.close()
    return jsonify({'answer': 'yes'})
@app.route('/sign', methods = ['POST'])
def sign():
    new = request.json
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * from users')
    records = cursor.fetchall()
    here = False
    user = {}
    for row in records:
        if row[1] == new['email'] and row[2] == new['password']:
            here = True
            return jsonify({'answer': 'correct', 'hash': row[8]})
    if not here:
        return jsonify({'answer': 'incorrect'})
@app.route('/registration', methods = ['POST'])
def registration():
    new = request.json
    con = sl.connect('instance/exercises.db')
    cursor = con.cursor()
    cursor.execute('SELECT * from users')
    records = cursor.fetchall()
    here = False
    for row in records:
        if row[1] == new['email'] or row[5] == new['id']:
            here = True
    if len(new['id'].split()) > 1:
        here = True
    if here:
        return jsonify({'answer': 'no'})
    else:
        cursor.execute('INSERT INTO users (name, email, password, score, avatar, id, about, balance, hash, friends) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (new['name'], new['email'], new['password'], 0, new['avatar'], new['id'], new['about'], 0, new['hash'], ''))
        con.commit()        
        return jsonify({'answer': 'yes'})
@app.route('/plus_score', methods = ['POST'])
def plus_score():
    new = request.json
    con = sl.connect('instance/exercises.db')
    cursor = con.cursor()
    cursor.execute('UPDATE users SET score = ? WHERE hash = ?', (int(new['score']) + 1, new['hash']))
    con.commit()
    return jsonify({'score': int(new['score']) + 1})
@app.route('/opti/', methods = ['GET'])
def opti():
    abc = request.args.get('hash', '') 
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    here = False
    for row in records:
        if str(row[8]) == abc:
            here = True
            return jsonify({'name': row[0], 'email': row[1], 'score': row[3], 'avatar': row[4], 'about': row[6], 'balance': row[7], 'id': row[5]})
    if not here:
        return jsonify({'answer': 'no'})
@app.route('/acc/', methods = ['GET'])
def acc():
    abc = request.args.get('hash', '')
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    here = False
    for row in records:
        if str(row[8]) == abc:
            here = True
            return jsonify({'score': row[3]})
    if not here:
        return jsonify({'answer': 'no'})
@app.route('/pub/', methods = ['GET'])
def pub():
    abc = request.args.get('id', '')
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    here = False
    for row in records:
        if str(row[8]) == abc:
            here = True
            return jsonify({'name': row[0], 'score': row[3], 'avatar': row[4]})
    if not here:
        return jsonify({'answer': 'no'})
@app.route('/chat/', methods = ['GET'])
def chat():
    abc = request.args.get('hash', '')
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[8]) == abc:
            id = row[5]
    cursor.execute('SELECT * FROM chats')
    records = cursor.fetchall()
    here = False
    results = []
    for row in records:
        if row[0] == id:
            here = True
            cursor.execute('SELECT * FROM users')
            records1 = cursor.fetchall()
            for row1 in records1:
                if row1[5] == row[1]:
                    name = row1[0]
                    id1 = row1[5]
                    avatar = row1[4]
                    my = 'yes'
                    results.append({'name': name, 'id': id1, 'avatar': avatar, 'read': row[4], 'my': my})
        elif row[1] == id:
            here = True
            cursor.execute('SELECT * FROM users')
            records1 = cursor.fetchall()
            for row1 in records1:
                if row1[5] == row[0]:
                    name = row1[0]
                    id1 = row1[5]
                    avatar = row1[4]
                    my = 'no'
                    results.append({'name': name, 'id': id1, 'avatar': avatar, 'read': row[4], 'my': my})
    result = []
    for i in range(len(results) - 1, -1, -1):
        result.append(results[i])
    if here:
        return jsonify(result)
    else:
        return jsonify({'answer': 'no'})
@app.route('/write/', methods = ['GET'])
def write():
    abc = request.args.get('id', '').split('***')
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[8]) == abc[0]:
            giver_id = row[5]
    cursor.execute('UPDATE chats SET read = ? WHERE giver_id = ? AND autor_id = ?', ('yes', giver_id, abc[1]))
    con.commit()
    cursor.execute('SELECT * FROM chats')
    records = cursor.fetchall()
    results = {'messages': []}
    for row in records:
        if (row[0] == abc[1] or row[0] == giver_id) and (row[1] == abc[1] or row[1] == giver_id):
            if row[0] == giver_id:
                results['messages'].append({'autor_id': abc[0], 'text': row[2], 'file': row[3], 'special': row[5]})
            else:
                results['messages'].append({'author_id': abc[1], 'text': row[2], 'file': row[3], 'special': row[5]})
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if row[5] == abc[1]:
            results.update({'avatar': row[4]})
            results.update({'name': row[0]})
    return results
@app.route('/writes', methods = ['POST'])
def writes():
    new = request.json
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[8]) == new['autor_id']:
            autor_id = row[5]
    cursor.execute('INSERT INTO chats(autor_id, giver_id, text, file, read, special) VALUES(?, ?, ?, ?, ?, ?);', (autor_id, new['giver_id'], new['text'], new['file'], 'no', 'no'))
    con.commit()
    return jsonify({'answer': 'yes'})
@app.route('/surch/', methods = ['GET'])
def surch():
    abc = request.args.get('id', '')
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    here = False
    records = cursor.fetchall()
    for row in records:
        if row[5] == abc:
            here = True
    if here:
        return jsonify({'answer': 'yes'})
    else:
        return jsonify({'answer': 'no'}) 
@app.route('/iceberg/', methods = ['GET'])
def iceberg():
    abc = request.args.get('hash', '')
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    here = False
    for row in records:
        if str(row[8]) == abc:
            here = True
            return jsonify({'balance': row[7]})
    if not here:
        return jsonify({'answer': 'no'})
@app.route('/buy', methods = ['POST'])
def buy():
    new = request.json
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    transaction = 0
    for i in new['nft']:
        transaction += ord(i)
    for i in new['hash']:
        transaction += ord(i)
    transaction += randint(1, 1000)
    for i in new['number']:
        transaction += ord(i)
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[8]) == new['hash']:
            id = row[5]
            balance = row[7]
    cursor.execute('INSERT INTO preds(id, how, sum, number, nft, ip) VALUES(?, ?, ?, ?, ?, ?)', (id, new['how'], new['sum'], new['number'], new['nft'], transaction))
    if new['sum'] != 0:
        cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (balance - int(new['how']), id))
    if new['nft'] != '':
        here = False
        cursor.execute('SELECT * FROM nft')
        records = cursor.fetchall()
        for row in records:
            if row[0] == new['number']:
                here = True
        if here == False:    
            cursor.execute('INSERT INTO nft(ip, owner, creator, nft, cost) VALUES(?, ?, ?, ?, ?)', (transaction, '', id, new['nft'], new['how']))
    con.commit()
    return jsonify({'answer': 'yes'})
@app.route('/preds', methods = ['GET'])
def preds():
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM preds')
    records = cursor.fetchall()
    results = []
    for row in records:
        results.append({'id': row[0], 'how': row[1], 'sum': row[2], 'number': row[3], 'nft': row[4], 'ip': row[5]})
    result = []
    con.commit()
    for i in range(len(results) - 1, -1, -1):
        result.append(results[i])
    return jsonify(result)
@app.route('/buyd', methods = ['POST'])
def buyd():
    id_buyer = ''
    new = request.json
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[8]) == new['id_buyer']:
            id_buyer = row[5]
    for row in records:
        if row[5] == id_buyer:
            bal = int(row[7])
    cursor.execute('SELECT * FROM price')
    records2 = cursor.fetchall()
    price = records2[0][1]
    price += ' ' + str(int(new['sum']) / int(new['how']))
    cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (bal +int(new['how']), id_buyer))
    cursor.execute('DELETE FROM preds WHERE id = ? AND ip = ?', (new['id_seller'], new['ip']))
    cursor.execute('UPDATE price SET price = ? WHERE id = ?', (price, 1))
    con.commit()
    return jsonify({'answer': 'yes'})
@app.route('/reduct', methods = ['POST'])
def reduct():
    new = request.json
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[8]) == new['hash']:
            if new['name'] != '':
                cursor.execute('UPDATE users SET name = ? WHERE hash = ?', (new['name'], new['hash']))
            else:
                cursor.execute('UPDATE users SET name = ? WHERE hash = ?', (row[0], new['hash']))
            if new['avatar'] != '':
                cursor.execute('UPDATE users SET avatar = ? WHERE hash = ?', (new['avatar'], new['hash']))
            else:
                cursor.execute('UPDATE users SET avatar = ? WHERE hash = ?', (row[4], new['hash']))
            if new['about'] != '':
                cursor.execute('UPDATE users SET about = ? WHERE hash = ?', (new['about'], new['hash']))
            else:
                cursor.execute('UPDATE users SET about = ? WHERE hash = ?', (row[6], new['hash']))
    con.commit()
    return jsonify({'answer': 'yes'})
@app.route('/nft', methods = ['POST'])
def nft():
    new = request.json
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[8]) == new['id_buyer']:
            id = row[5]
    for row in records:
        if row[5] == id:
            buyer_bal = int(row[7])
        elif row[5] == new['id_seller']:
            seller_bal = int(row[7])
    cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (seller_bal + new['how'], new['id_seller']))
    cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (buyer_bal - new['how'], id))
    cursor.execute('DELETE FROM preds WHERE ip = ? AND id = ?', (new['ip'], new['id_seller']))
    cursor.execute('UPDATE nft SET owner = ? WHERE ip = ?', (id, new['ip']))
    cursor.execute('UPDATE nft SET cost = ? WHERE ip = ?', (new['how'], new['ip']))
    con.commit()
    return jsonify({'answer': 'ok'})
@app.route('/my_lent/', methods = ['GET'])
def my_lent():
    abc = request.args.get('hash', '')
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[8]) == abc:
            id = row[5]
            autor = row[0]
            score = row[3]
            avatar = row[4]
    result = []
    cursor.execute('SELECT * FROM lent')
    records = cursor.fetchall()
    for row in records:
        if row[0] == abc:
            result.append({'ip': row[3], 'autor': autor, 'text': row[1], 'score': score, 'avatar': avatar, 'file': row[2], 'id': id, 'likes': row[4]})
    results = []
    for i in range(len(result) - 1, -1, -1):
        results.append(result[i])
    return jsonify(results)
@app.route('/my_nft/', methods = ['GET'])
def my_nft():
    abc = request.args.get('hash', '')
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[8]) == abc:
            id = row[5]
    cursor.execute('SELECT * FROM nft')
    records = cursor.fetchall()
    result = []
    for row in records:
        if row[1] == id:
            result.append({'ip': row[0], 'owner': row[1], 'creator': row[2], 'nft': row[3], 'cost': row[4]})
    return jsonify(result)
@app.route('/gift', methods = ['POST'])
def gift():
    new = request.json
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    here = False
    cursor.execute('SELECT * FROM nft')
    records = cursor.fetchall()
    for row in records:
        if row[0] == new['number']:
            nft = row[3]
            cost = row[4]
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if row[5] == new['adress']:
            here = True
        elif str(row[8]) == new['hash']:
            id = row[5]
    if here == True:
        cursor.execute('UPDATE nft SET owner = ? WHERE ip = ?', (new['adress'], new['number']))
        cursor.execute('INSERT INTO chats (autor_id, giver_id, text, file, read, special) VALUES(?, ?, ?, ?, ?, ?)', (id, new['adress'], 'Пользователь ' + id + ' подарил тебе NFT номер ' + str(new['number']) + ' стоимостью ' + str(cost) + ' ICE', nft, 'no', 'nft'))
        con.commit()
        return jsonify({'answer': 'yes'})
    else:
        return jsonify({'answer': 'no'})
@app.route('/buy_nft', methods = ['POST'])
def buy_nft():
    new = request.json
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[8]) == new['hash']:
            id = row[5]
    cursor.execute('INSERT INTO preds(id, how, sum, number, nft, ip) VALUES(?, ?, ?, ?, ?, ?)', (id, new['how'], 0, '', new['nft'], new['ip']))
    cursor.execute('UPDATE nft SET cost = ? WHERE ip = ?', (new['how'], new['ip']))
    cursor.execute('UPDATE nft SET owner = ? WHERE ip = ?', ('', new['ip']))
    con.commit()
    return jsonify({'answer': 'yes'})
@app.route('/gift_ice', methods = ['POST'])
def gift_ice():
    new = request.json
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    here = False
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    balance_giver = 0
    balance_seller = 0
    for row in records:
        if str(row[8]) == new['id_seller']:
            here = True
            id = row[5]
            balance_seller = row[7]
        elif str(row[5]) == new['id_giver']:
            balance_giver = row[7]
    if here == False:
        return jsonify({'answer': 'no'})
    else:
        cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (int(new['how']) + int(balance_giver), new['id_giver']))
        cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (int(balance_seller) - int(new['how']), id))
        cursor.execute('INSERT INTO chats (autor_id, giver_id, text, file, read, special) VALUES(?, ?, ?, ?, ?, ?)', (id, new['id_giver'], 'Пользователь ' + id + ' перевел тебе ' + new['how'] + ' ICE', 'no', 'no', 'ice'))
        con.commit()
        return jsonify({'answer': 'yes'})
@app.route('/account', methods = ['GET'])
def account():
    abc = request.args.get('id', '')
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if row[5] == abc:
            return jsonify({'name': row[0], 'score': row[3], 'avatar': row[4], 'about': row[6], 'balance': row[7]})
@app.route('/your_lent', methods = ['GET'])
def your_lent():
    abc = request.args.get('id', '')
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if row[5] == abc:
            autor = row[1]
            hash = str(row[8])
            score = row[3]
            avatar =row[4]
    cursor.execute('SELECT * FROM lent')
    results = []
    records = cursor.fetchall()
    for row in records:
        if str(row[0]) == hash:
            results.append({'number': row[3], 'autor': autor, 'text': row[1], 'score': score, 'avatar': avatar, 'file': row[2], 'likes': row[4]})
    result = []
    for i in range(len(results) - 1, -1, -1):
        result.append(results[i])
    return jsonify(result)
@app.route('/your_nft', methods = ['GET'])
def your_nft():
    abc = request.args.get('id', '')
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM nft')
    records = cursor.fetchall()
    result = []
    for row in records:
        if row[1] == abc:
            result.append({'ip': row[0], 'creator': row[2], 'nft': row[3], 'cost': row[4]})
    return jsonify(result)
@app.route('/friend', methods = ['POST'])
def friend():
    new = request.json
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[8]) == new['hash']:
            id = row[5]
            file = row[4]
    cursor.execute('INSERT INTO chats(autor_id, giver_id, text, file, read, special) VALUES(?, ?, ?, ?, ?, ?)', (id, new['id'], 'Пользователь ' + new['id'] + ' хочет добавить тебя в друзья. Добавить?', file, 'no', 'friend'))
    con.commit()
    return jsonify({'answer': 'yes'})
@app.route('/yes_friend', methods = ['POST'])
def yes_friend():
    new = request.json
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[8]) == new['id1']:
            id = row[5]
            my_friends = row[9].split()
        elif row[5] == new['id2']:
            your_friends = row[9].split()
    if new['id2'] not in my_friends:
        cursor.execute('UPDATE users SET friends = ? WHERE id = ?', (' '.join(my_friends) + ' ' + new['id2'], id))
    if id not in your_friends:
        cursor.execute('UPDATE users SET friends = ? WHERE id = ?', (' '.join(your_friends) + ' ' + id, new['id2']))
    con.commit()
    return jsonify({'answer': 'yes'})
@app.route('/my_friends/', methods = ['GET'])
def my_friends():
    abc = request.args.get('hash', '')
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    result = []
    records = cursor.fetchall()
    for row in records:
        if str(row[8]) == abc:
            for i in row[9].split():
                cursor.execute('SELECT * FROM users')
                records1 = cursor.fetchall()
                for row1 in records1:
                    if row1[5] == i:
                        result.append({'name': row1[0], 'avatar': row1[4], 'id': row1[5]})
    return jsonify(result)
@app.route('/your_friends/', methods = ['GET'])
def your_friends():
    abc = request.args.get('id', '')
    con = sl.connect('instance/exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    result = []
    records = cursor.fetchall()
    for row in records:
        if row[5] == abc:
            for i in row[9].split():
                cursor.execute('SELECT * FROM users')
                records1 = cursor.fetchall()
                for row1 in records1:
                    if row1[5] == i:
                        result.append({'name': row1[0], 'avatar': row1[4], 'id': row1[5]})
    return jsonify(result)
if __name__ == '__main__':
    app.run(debug = False, port = 5000, host = '0.0.0.0')
