from flask import Flask, request, jsonify
import hashlib
import json
from time import time
from flask_cors import CORS
import sqlite3 as sl
from random import randint
import requests
con = sl.connect('./exercises.db', check_same_thread = False)
cursor = con.cursor()
#cursor.execute('DROP TABLE users')
#cursor.execute('DROP TABLE lent')
#cursor.execute('DROP TABLE chats')
#cursor.execute('DROP TABLE price')

#эмитатор
#cursor.execute('DROP TABLE balances')
#cursor.execute('DROP TABLE nfts')
#cursor.execute('DROP TABLE preds')

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
if ('users', ) not in tables:
    con.execute('CREATE TABLE users (name TEXT, email TEXT, password INT, avatar TEXT, id TEXT, about TEXT, hash INT, friends TEXT, bans INT, status TEXT)')
if ('lent', ) not in tables:
    con.execute('CREATE TABLE lent(id TEXT, text TEXT, file TEXT, ip INT, likes INT, type TEXT)')
if ('chats', ) not in tables:
    con.execute('CREATE TABLE chats(autor_id TEXT, giver_id TEXT, text TEXT, file TEXT, read TEXT, special TEXT, type TEXT);')
if ('price', ) not in tables:
    con.execute('CREATE TABLE price(id INT, price TEXT);')

#эмитатор
if ('balances', ) not in tables:
    con.execute('CREATE TABLE balances (hash FLOAT, balance INT);')
if ('nfts', ) not in tables:
    con.execute('CREATE TABLE nfts (token FLOAT, owner FLOAT, creator TEXT, cost INT, nft TEXT);')
if ('preds', ) not in tables:
    con.execute('CREATE TABLE preds (token FLOAT, owner FLOAT, creator TEXT, cost INT, sum INT, nft TEXT)')
con.execute('INSERT INTO balances (hash, balance) VALUES (?, ?)', (6.574042824760661e+28, 1000000))


con.execute('INSERT INTO price(id, price) VALUES(?, ?);', (1, '2.0'))
con.execute('INSERT INTO users(name, email, password, avatar, id, about, hash, friends, bans, status) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', ('Sophie', 'krismironova04@mail.ru', 1.0672147442793281e+26, '', 'Sophie', 'Твой друг и помощник в социальной сети Друзья 2.0', 6.574042824760661e+28, '', 0, 'active'))
con.commit()
class Block:
    def __init__(self, index, transactions, previous_hash, nonce=0):
        self.index = index
        self.timestamp = time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()
        self.unconfirmed_transactions = []
        self.nfts = {}  # Хранит NFT в формате {token_id: owner}
        self.chain = []
        self.peers = set()  # Сетевые адреса других нод (например, "http://192.168.1.2:5000")
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False
        if not self.is_valid_proof(block, proof):
            return False
        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, block_hash):
        return block_hash.startswith('0000')  # Простое PoW

    def mine(self):
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block
        new_block = Block(
            index=last_block.index + 1,
            transactions=self.unconfirmed_transactions,
            previous_hash=last_block.hash
        )

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return new_block.index

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0000'):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    @property
    def last_block(self):
        return self.chain[-1]
    def mint_nft(self, owner, token_id, metadata):
        if token_id in self.nfts:
            return False  # NFT уже существует
        self.nfts[token_id] = {
            "owner": owner,
            "metadata": metadata  # Например, {"name": "My NFT", "image": "ipfs://..."}
        }
        self.unconfirmed_transactions.append({
            "type": "mint",
            "token_id": token_id,
            "owner": owner
        })
        return True

    def transfer_nft(self, sender, receiver, token_id):
        if token_id not in self.nfts:
            return False  # NFT не существует
        if self.nfts[token_id]["owner"] != sender:
            return False  # Неправильный владелец
        self.nfts[token_id]["owner"] = receiver
        self.nfts[token_id]['metadata']['status'] = 'no'
        self.unconfirmed_transactions.append({
            "type": "transfer",
            "token_id": token_id,
            "from": sender,
            "to": receiver
        })
        return True
    def register_peer(self, address):
        """Добавляем новую ноду в сеть"""
        self.peers.add(address)

    def sync_chain(self):
        """Синхронизация цепи с самой длинной версией из сети"""
        longest_chain = None
        max_length = len(self.chain)

        for peer in self.peers:
            response = requests.get(f"{peer}/chain")  # Запрашиваем цепь у других нод
            if response.status_code == 200:
                peer_chain = response.json()["chain"]
                if len(peer_chain) > max_length and self.is_chain_valid(peer_chain):
                    max_length = len(peer_chain)
                    longest_chain = peer_chain

        if longest_chain:
            self.chain = longest_chain
            return True
        return False
    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0000'):  # Хеш должен начинаться с 4 нулей
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash
    def is_chain_valid(self, chain):
        for i in range(1, len(chain)):
            if chain[i]["previous_hash"] != chain[i-1]["hash"]:
                return False
            if not chain[i]["hash"].startswith('0000'):  # Проверка PoW
                return False
        return True
app = Flask(__name__)
cors = CORS(app)
blockchain = Blockchain()
blockchain.mint_nft('3.0211397684608867e+28', '1', {'how': '1000000', 'sum': '0', 'number': '', 'nft': '', 'status': 'no'})
@app.route('/lent/', methods = ['GET'])
def lent():
    abc = request.args.get('number', '') 
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    result = {}
    cursor.execute('SELECT * from lent')
    records = cursor.fetchall()
    if len(records) - int(abc) <= 0:
        result = {'number': 0, 'autor': 'EasyPass', 'text': 'Ты посмотрел все публикации!'}
    else:
        for row in records:
            if len(records) - int(abc) == row[3]:
                cursor.execute('SELECT * FROM users')
                records1 = cursor.fetchall()
                for row1 in records1:
                    if str(row1[6]) == row[0]:
                        autor = row1[0]
                        avatar = row1[3]
                        id = row1[4]
                        result = {'number': row[3], 'autor': autor, 'text': row[1], 'avatar': avatar, 'file': row[2], 'id': id, 'likes': row[4], 'type': row[5]}
    return jsonify(result)
@app.route('/publicate', methods = ['POST'])
def publicate():
    new = request.json
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM lent')
    records = cursor.fetchall()
    cursor.execute('INSERT INTO lent (id, text, file, ip, likes, type) VALUES (?, ?, ?, ?, ?, ?)', (new['hash'], new['text'], new['file'], len(records)+1, 0, new['type']))
    con.commit()
    con.close()
    return jsonify({'answer': 'yes'})
@app.route('/sign', methods = ['POST'])
def sign():
    new = request.json
    con = sl.connect('./exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * from users')
    records = cursor.fetchall()
    here = False
    user = {}
    for row in records:
        if row[1] == new['email'] and row[2] == new['password'] and row[9] == 'active':
            here = True
            return jsonify({'answer': 'correct', 'hash': row[6]})
        elif row[1] == new['email'] and row[2] == new['password'] and row[9] == 'baned':
            here = True
            return jsonify({'answer': 'baned'})
    if not here:
        return jsonify({'answer': 'incorrect'})
@app.route('/registration', methods = ['POST'])
def registration():
    new = request.json
    con = sl.connect('exercises.db')
    cursor = con.cursor()
    cursor.execute('SELECT * from users')
    records = cursor.fetchall()
    here = False
    for row in records:
        if row[1] == new['email'] or row[4] == new['id']:
            here = True
    if len(new['id'].split()) > 1:
        here = True
    if here:
        return jsonify({'answer': 'no'})
    else:
        cursor.execute('INSERT INTO users (name, email, password, avatar, id, about, hash, friends, bans, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (new['name'], new['email'], new['password'], new['avatar'], new['id'], new['about'], new['hash'], '', 0, 'active'))
        con.commit()        
        return jsonify({'answer': 'yes'})
@app.route('/opti/', methods = ['GET'])
def opti():
    abc = request.args.get('hash', '') 
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    here = False
    for row in records:
        if str(row[6]) == abc:
            here = True
            return jsonify({'name': row[0], 'email': row[1], 'avatar': row[3], 'about': row[5], 'id': row[4]})
    if not here:
        return jsonify({'answer': 'no'})
@app.route('/pub/', methods = ['GET'])
def pub():
    abc = request.args.get('id', '')
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    here = False
    for row in records:
        if str(row[6]) == abc:
            here = True
            return jsonify({'name': row[0], 'avatar': row[3]})
    if not here:
        return jsonify({'answer': 'no'})
@app.route('/chat/', methods = ['GET'])
def chat():
    abc = request.args.get('hash', '')
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[6]) == abc:
            id = row[4]
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
                if row1[4] == row[1]:
                    name = row1[0]
                    id1 = row1[4]
                    avatar = row1[3]
                    my = 'yes'
                    results.append({'name': name, 'id': id1, 'avatar': avatar, 'read': row[4], 'my': my})
        elif row[1] == id:
            here = True
            cursor.execute('SELECT * FROM users')
            records1 = cursor.fetchall()
            for row1 in records1:
                if row1[4] == row[0]:
                    name = row1[0]
                    id1 = row1[4]
                    avatar = row1[3]
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
    abc = request.args.get('id', '').split(' ')
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[6]) == abc[0]:
            giver_id = row[4]
    cursor.execute('UPDATE chats SET read = ? WHERE giver_id = ? AND autor_id = ?', ('yes', giver_id, abc[1]))
    con.commit()
    cursor.execute('SELECT * FROM chats')
    records = cursor.fetchall()
    results = {'messages': []}
    for row in records:
        if (row[0] == abc[1] or row[0] == giver_id) and (row[1] == abc[1] or row[1] == giver_id):
            if row[0] == giver_id:
                results['messages'].append({'autor_id': abc[0], 'text': row[2], 'file': row[3], 'special': row[5], 'type': row[6]})
            else:
                results['messages'].append({'author_id': abc[1], 'text': row[2], 'file': row[3], 'special': row[5], 'type': row[6]})
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if row[4] == abc[1]:
            results.update({'avatar': row[3]})
            results.update({'name': row[0]})
    return results
@app.route('/writes', methods = ['POST'])
def writes():
    new = request.json
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[6]) == new['autor_id']:
            autor_id = row[4]
    cursor.execute('INSERT INTO chats(autor_id, giver_id, text, file, read, special, type) VALUES(?, ?, ?, ?, ?, ?, ?);', (autor_id, new['giver_id'], new['text'], new['file'], 'no', 'no', new['type']))
    con.commit()
    return jsonify({'answer': 'yes'})
@app.route('/surch/', methods = ['GET'])
def surch():
    abc = request.args.get('id', '')
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    here = False
    records = cursor.fetchall()
    for row in records:
        if row[4] == abc:
            here = True
    if here:
        return jsonify({'answer': 'yes'})
    else:
        return jsonify({'answer': 'no'}) 
@app.route('/iceberg/', methods = ['GET'])
def iceberg():
    abc = request.args.get('hash', '')
    result = 0
    '''for i in range(len(blockchain.chain)):
        for j in range(len(blockchain.chain[i].transactions)):
            if blockchain.chain[i].transactions[j]['type'] == 'mint' and blockchain.chain[i].transactions[j]['owner'] == abc:
                token = blockchain.chain[i].transactions[j]['token_id']
                for k in blockchain.nfts:
                    if k == token and blockchain.nfts[k]['owner'] == abc and blockchain.nfts[k]['metadata']['nft'] == '' and blockchain.nfts[k]['metadata']['status'] == 'no':
                        result += int(blockchain.nfts[k]['metadata']['how'])
                    elif k == token and blockchain.nfts[k]['owner'] == abc and blockchain.nfts[k]['metadata']['nft'] == '' and blockchain.nfts[k]['metadata']['status'] == 'sale':
                        result -= int(blockchain.nfts[k]['metadata']['how'])
            elif blockchain.chain[i].transactions[j]['type'] == 'transfer' and blockchain.chain[i].transactions[j]['from'] == abc:
                token = blockchain.chain[i].transactions[j]['token_id']
                for k in blockchain.nfts:
                    if k == token and blockchain.nfts[k]['metadata']['nft'] == '':
                        result -= int(blockchain.nfts[k]['metadata']['how'])
                    elif k == token and blockchain.nfts[k]['metadata']['nft'] != '':
                        result += int(blockchain.nfts[k]['metadata']['how'])
            elif blockchain.chain[i].transactions[j]['type'] == 'transfer' and blockchain.chain[i].transactions[j]['to'] == abc:
                token = blockchain.chain[i].transactions[j]['token_id']
                for k in blockchain.nfts:
                    if k == token and blockchain.nfts[k]['metadata']['nft'] == '':
                        result += int(blockchain.nfts[k]['metadata']['how'])
                    elif k == token and blockchain.nfts[k]['metadata']['nft'] != '':
                        result -= int(blockchain.nfts[k]['metadata']['how'])'''
    
    #эмитатор
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    here = False
    cursor.execute('SELECT * FROM balances')
    records = cursor.fetchall()
    for row in records:
        if str(row[0]) == abc:
            here = True
            result = row[1]
    if here == False:
        cursor.execute('INSERT INTO balances (hash, balance) VALUES (?, ?)', (float(abc), 0))
    con.commit()


    return jsonify({'balance': result})
@app.route('/reduct', methods = ['POST'])
def reduct():
    new = request.json
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[6]) == new['hash']:
            if new['name'] != '':
                cursor.execute('UPDATE users SET name = ? WHERE hash = ?', (new['name'], new['hash']))
            else:
                cursor.execute('UPDATE users SET name = ? WHERE hash = ?', (row[0], new['hash']))
            if new['avatar'] != '':
                cursor.execute('UPDATE users SET avatar = ? WHERE hash = ?', (new['avatar'], new['hash']))
            else:
                cursor.execute('UPDATE users SET avatar = ? WHERE hash = ?', (row[3], new['hash']))
            if new['about'] != '':
                cursor.execute('UPDATE users SET about = ? WHERE hash = ?', (new['about'], new['hash']))
            else:
                cursor.execute('UPDATE users SET about = ? WHERE hash = ?', (row[5], new['hash']))
    con.commit()
    return jsonify({'answer': 'yes'})
@app.route('/my_lent/', methods = ['GET'])
def my_lent():
    abc = request.args.get('hash', '')
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[6]) == abc:
            id = row[4]
            autor = row[0]
            avatar = row[3]
    result = []
    cursor.execute('SELECT * FROM lent')
    records = cursor.fetchall()
    for row in records:
        if row[0] == abc:
            result.append({'ip': row[3], 'autor': autor, 'text': row[1], 'avatar': avatar, 'file': row[2], 'id': id, 'likes': row[4], 'type': row[5]})
    results = []
    for i in range(len(result) - 1, -1, -1):
        results.append(result[i])
    return jsonify(results)
@app.route('/account', methods = ['GET'])
def account():
    abc = request.args.get('id', '')
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if row[4] == abc:
            return jsonify({'name': row[0], 'avatar': row[3], 'about': row[5]})
@app.route('/your_lent', methods = ['GET'])
def your_lent():
    abc = request.args.get('id', '')
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if row[4] == abc:
            autor = row[0]
            hash = str(row[6])
            avatar = row[3]
    cursor.execute('SELECT * FROM lent')
    results = []
    records = cursor.fetchall()
    for row in records:
        if str(row[0]) == hash:
            results.append({'number': row[3], 'autor': autor, 'text': row[1], 'avatar': avatar, 'file': row[2], 'likes': row[4], 'type': row[5]})
    result = []
    for i in range(len(results) - 1, -1, -1):
        result.append(results[i])
    return jsonify(result)
@app.route('/friend', methods = ['POST'])
def friend():
    new = request.json
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[6]) == new['hash']:
            id = row[4]
            file = row[3]
    cursor.execute('INSERT INTO chats(autor_id, giver_id, text, file, read, special) VALUES(?, ?, ?, ?, ?, ?)', (id, new['id'], 'Пользователь ' + id + ' хочет добавить тебя в друзья. Добавить?', file, 'no', 'friend'))
    con.commit()
    return jsonify({'answer': 'yes'})
@app.route('/yes_friend', methods = ['POST'])
def yes_friend():
    new = request.json
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[6]) == new['id1']:
            id = row[4]
            my_friends = row[7].split()
        elif row[4] == new['id2']:
            your_friends = row[7].split()
    if new['id2'] not in my_friends:
        cursor.execute('UPDATE users SET friends = ? WHERE id = ?', (' '.join(my_friends) + ' ' + new['id2'], id))
    if id not in your_friends:
        cursor.execute('UPDATE users SET friends = ? WHERE id = ?', (' '.join(your_friends) + ' ' + id, new['id2']))
    con.commit()
    return jsonify({'answer': 'yes'})
@app.route('/my_friends/', methods = ['GET'])
def my_friends():
    abc = request.args.get('hash', '')
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    result = []
    records = cursor.fetchall()
    for row in records:
        if str(row[6]) == abc:
            for i in row[7].split():
                cursor.execute('SELECT * FROM users')
                records1 = cursor.fetchall()
                for row1 in records1:
                    if row1[4] == i:
                        result.append({'name': row1[0], 'avatar': row1[3], 'id': row1[4]})
    return jsonify(result)
@app.route('/your_friends/', methods = ['GET'])
def your_friends():
    abc = request.args.get('id', '')
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    result = []
    records = cursor.fetchall()
    for row in records:
        if row[4] == abc:
            for i in row[7].split():
                cursor.execute('SELECT * FROM users')
                records1 = cursor.fetchall()
                for row1 in records1:
                    if row1[4] == i:
                        result.append({'name': row1[0], 'avatar': row1[3], 'id': row1[4]})
    return jsonify(result)
@app.route('/avatar/', methods = ['GET'])
def avatar():
    abc = request.args.get('hash', '')
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    here = False
    result = {}
    for row in records:
        if str(row[6]) == abc:
            here = True
            result = {'avatar': row[3]}
    if here == False:
        result = {'answer': 'no'}
    return jsonify(result)
@app.route('/mine', methods=['GET'])
def mine():
    index = blockchain.mine()
    response = {'message': f'Block #{index} mined!'}
    return jsonify(response), 200
@app.route('/mint', methods=['POST'])
def mint_nft():
    data = request.get_json()
    balance = 0
    '''for i in  blockchain.nfts:
        if blockchain.nfts[i]['owner'] == data['owner'] and blockchain.nfts[i]['metadata']['nft'] == '' and blockchain.nfts[i]['metadata']['status'] == 'no':
            balance += int(blockchain.nfts[i]['metadata']['how'])
        elif blockchain.nfts[i]['owner'] == data['owner'] and blockchain.nfts[i]['metadata']['nft'] == '' and blockchain.nfts[i]['metadata']['status'] == 'sale':
            balance -= int(blockchain.nfts[i]['metadata']['how'])
    if data['metadata']['nft'] == '' and int(data['metadata']['how']) > balance:
        return 'Low balance', 400
    required = ["owner", "token_id", "metadata"]
    if not all(k in data for k in required):
        return "Missing data", 400
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[6]) == data['metadata']['creator']:
            data['metadata']['creator'] = row[4]
    success = blockchain.mint_nft(data["owner"], data["token_id"], data["metadata"])
    if not success:
        return "NFT already exists", 400'''
    
    #эмитатор
    balance = 0
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if str(row[6]) == data['owner']:
            creator = row[4]
    records = cursor.execute('SELECT * FROM balances')
    for row in records:
        if str(row[0]) == data['owner']:
            balance = row[1]
    if balance < int(data['metadata']['how']) and data['metadata']['nft'] == '':
        return 'Low money', 400
    if data['metadata']['nft'] == '':
        cursor.execute('UPDATE balances SET balance = ? WHERE hash = ?', (balance - float(data['metadata']['how']), float(data['owner'])))
        cursor.execute('SELECT * FROM price')
        records = cursor.fetchall()
        cursor.execute('INSERT INTO price (id, price) VALUES (?, ?)', (len(records) + 1, int(data['metadata']['sum']) / int(data['metadata']['how'])))
    else:
        cursor.execute('INSERT INTO nfts (token, owner, creator, cost, nft) VALUES (?, ?, ?, ?, ?)', (data['token_id'], data['owner'], creator, data['metadata']['how'], data['metadata']['nft']))
    cursor.execute('INSERT INTO preds (token, owner, creator, cost, sum, nft) VALUES (?, ?, ?, ?, ?, ?)', (data['token_id'], data['owner'], creator, data['metadata']['how'], data['metadata']['sum'], data['metadata']['nft']))
    con.commit()


    return jsonify({"message": "NFT minted!"}), 200
@app.route('/transfer', methods=['POST'])
def transfer_nft():
    data = request.get_json()
    '''required = ["sender", "receiver", "token_id"]
    if not all(k in data for k in required):
        return "Missing data", 400
    result = 0
    for i in range(len(blockchain.chain)):
        for j in range(len(blockchain.chain[i].transactions)):
            if blockchain.chain[i].transactions[j]['type'] == 'mint' and blockchain.chain[i].transactions[j]['owner'] == data['receiver']:
                token = blockchain.chain[i].transactions[j]['token_id']
                for k in blockchain.nfts:
                    if k == token and blockchain.nfts[k]['owner'] == data['receiver'] and blockchain.nfts[k]['metadata']['nft'] == '' and blockchain.nfts[k]['metadata']['status'] == 'no':
                        result += int(blockchain.nfts[k]['metadata']['how'])
                    elif k == token and blockchain.nfts[k]['owner'] == data['receiver'] and blockchain.nfts[k]['metadata']['nft'] == '' and blockchain.nfts[k]['metadata']['status'] == 'sale':
                        result -= int(blockchain.nfts[k]['metadata']['how'])
            elif blockchain.chain[i].transactions[j]['type'] == 'transfer' and blockchain.chain[i].transactions[j]['from'] == data['receiver']:
                token = blockchain.chain[i].transactions[j]['token_id']
                for k in blockchain.nfts:
                    if k == token and blockchain.nfts[k]['metadata']['nft'] == '':
                        result -= int(blockchain.nfts[k]['metadata']['how'])
                    elif k == token and blockchain.nfts[k]['metadata']['nft'] != '':
                        result += int(blockchain.nfts[k]['metadata']['how'])
            elif blockchain.chain[i].transactions[j]['type'] == 'transfer' and blockchain.chain[i].transactions[j]['to'] == data['receiver']:
                token = blockchain.chain[i].transactions[j]['token_id']
                for k in blockchain.nfts:
                    if k == token and blockchain.nfts[k]['metadata']['nft'] == '':
                        result += int(blockchain.nfts[k]['metadata']['how'])
                    elif k == token and blockchain.nfts[k]['metadata']['nft'] != '':
                        result -= int(blockchain.nfts[k]['metadata']['how'])
    if result < data['how'] and data['nft'] != '':
        return 'Low money', 400
    success = blockchain.transfer_nft(data["sender"], data["receiver"], data["token_id"])
    if not success:
        return "Transfer failed", 400'''
    
    #эмитатор
    balance_receiver = 0
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM balances')
    records1 = cursor.fetchall()
    for row1 in records1:
        if str(row1[0]) == data['receiver']:
            balance_receiver = row1[1]
        elif row1[0] == data['sender']:
            balance_sender = row1[1]
    if  data['nft'] == '':
        cursor.execute('UPDATE balances SET balance = ? WHERE hash = ?', (balance_receiver + int(data['how']), float(data['receiver'])))
    elif  data['nft'] != '' and balance_receiver >= int(data['how']):
        cursor.execute('UPDATE nfts SET owner = ? WHERE token = ?', (float(data['receiver']), float(data['token_id'])))
        cursor.execute('UPDATE balances SET balance = ? WHERE hash = ?', (balance_sender + int(data['how']), float(data['sender'])))
        cursor.execute('UPDATE balances SET balance = ? WHERE hash = ?', (balance_receiver - int(data['how']), float(data['receiver'])))
    else:
        return 'Low money', 400
    cursor.execute('DELETE FROM preds WHERE token = ?', (float(data['token_id']), ))
    con.commit()


    return jsonify({"message": "NFT transferred!"}), 200
@app.route('/nfts', methods=['GET'])
def get_all_nfts():
    result = {}
    '''for i in blockchain.nfts:
        if blockchain.nfts[i]['metadata']['status'] == 'sale':
            result.update({i: blockchain.nfts[i]})'''
    
    #эмитатор
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM preds')
    records = cursor.fetchall()
    for row in records:
        result.update({row[0]: {'owner': row[1], 'metadata': {'creator': row[2], 'how': row[3], 'sum': row[4], 'nft': row[5]}}})


    return jsonify(result), 200 
@app.route('/peers', methods=['GET'])
def get_peers():
    return jsonify(list(blockchain.peers)), 200

@app.route('/register_peer', methods=['POST'])
def register_peer():
    data = request.get_json()
    blockchain.register_peer(data["address"])
    return jsonify({"message": "Peer added"}), 200

@app.route('/sync', methods=['GET'])
def sync():
    if blockchain.sync_chain():
        return jsonify({"message": "Chain synced"}), 200
    return jsonify({"message": "Sync failed"}), 400
@app.route('/my_nft/', methods = ['GET'])
def my_nft():
    result = []
    abc = request.args.get('hash', '')
    '''for i in blockchain.nfts:
        if str(blockchain.nfts[i]['owner']) == abc and blockchain.nfts[i]['metadata']['nft'] != '' and blockchain.nfts[i]['metadata']['status'] == 'no':
            result.append({'nft': blockchain.nfts[i]['metadata']['nft'], 'creator': blockchain.nfts[i]['metadata']['creator'], 'cost': blockchain.nfts[i]['metadata']['how'], 'ip': i})'''
    

    #эмитатор
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    preds = []
    cursor.execute('SELECT * FROM preds')
    records = cursor.fetchall()
    for row in records:
        preds.append(row[0])
    cursor.execute('SELECT * FROM nfts')
    records = cursor.fetchall()
    for row in records:
        if str(row[1]) == abc and (row[0] not in preds):
            result.append({'nft': row[4], 'creator': row[2], 'cost': row[3], 'ip': row[0]})


    return jsonify(result)
@app.route('/your_iceberg/', methods = ['GET'])
def your_iceberg():
    abc = request.args.get('id', '')
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    result= 0
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if row[4] == abc:
            abc = str(row[6])
    '''for i in range(len(blockchain.chain)):
        for j in range(len(blockchain.chain[i].transactions)):
            if blockchain.chain[i].transactions[j]['type'] == 'mint' and blockchain.chain[i].transactions[j]['owner'] == abc:
                token = blockchain.chain[i].transactions[j]['token_id']
                for k in blockchain.nfts:
                    if k == token and blockchain.nfts[k]['owner'] == abc and blockchain.nfts[k]['metadata']['nft'] == '' and blockchain.nfts[k]['metadata']['status'] == 'no':
                        result += int(blockchain.nfts[k]['metadata']['how'])
                    elif k == token and blockchain.nfts[k]['owner'] == abc and blockchain.nfts[k]['metadata']['nft'] == '' and blockchain.nfts[k]['metadata']['status'] == 'sale':
                        result -= int(blockchain.nfts[k]['metadata']['how'])
            elif blockchain.chain[i].transactions[j]['type'] == 'transfer' and blockchain.chain[i].transactions[j]['from'] == abc:
                token = blockchain.chain[i].transactions[j]['token_id']
                for k in blockchain.nfts:
                    if k == token and blockchain.nfts[k]['metadata']['nft'] == '':
                        result -= int(blockchain.nfts[k]['metadata']['how'])
                    elif k == token and blockchain.nfts[k]['metadata']['nft'] != '':
                        result += int(blockchain.nfts[k]['metadata']['how'])
            elif blockchain.chain[i].transactions[j]['type'] == 'transfer' and blockchain.chain[i].transactions[j]['to'] == abc:
                token = blockchain.chain[i].transactions[j]['token_id']
                for k in blockchain.nfts:
                    if k == token and blockchain.nfts[k]['metadata']['nft'] == '':
                        result += int(blockchain.nfts[k]['metadata']['how'])
                    elif k == token and blockchain.nfts[k]['metadata']['nft'] != '':
                        result -= int(blockchain.nfts[k]['metadata']['how'])'''
    
    #эмитатор
    cursor.execute('SELECT * FROM balances')
    records = cursor.fetchall()
    for row in records:
        if str(row[0]) == abc:
            result = row[1]


    return jsonify({'balance': result})
@app.route('/your_nft/', methods = ['GET'])
def your_nft():
    abc = request.args.get('id', '')
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if row[4] == abc:
            abc = str(row[6])
    result = []
    '''for i in blockchain.nfts:
        if str(blockchain.nfts[i]['owner']) == abc and blockchain.nfts[i]['metadata']['nft'] != '' and blockchain.nfts[i]['metadata']['status'] == 'no':
            result.append({'nft': blockchain.nfts[i]['metadata']['nft'], 'creator': blockchain.nfts[i]['metadata']['creator'], 'cost': blockchain.nfts[i]['metadata']['how'], 'ip': i})'''
    

    #эмитатор
    preds = []
    cursor.execute('SELECT * FROM preds')
    records = cursor.fetchall()
    for row in records:
        preds.append(row[0])
    cursor.execute('SELECT * FROM nfts')
    records = cursor.fetchall()
    for row in records:
        if str(row[1]) == abc and (int(row[0]) not in preds):
            result.append({'nft': row[4], 'creator': row[2], 'cost': row[3], 'ip': row[0]})


    return jsonify(result)
@app.route('/gift_ice', methods = ['POST'])
def gift_ice():
    new = request.json
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if row[4] == new['id_giver']:
            reciever = row[6]
        elif str(row[6]) == new['id_seller']:
            author = row[4]
    abc = new['id_seller']
    '''result = 0
    for i in range(len(blockchain.chain)):
        for j in range(len(blockchain.chain[i].transactions)):
            if blockchain.chain[i].transactions[j]['type'] == 'mint' and blockchain.chain[i].transactions[j]['owner'] == abc:
                token = blockchain.chain[i].transactions[j]['token_id']
                for k in blockchain.nfts:
                    if k == token and blockchain.nfts[k]['owner'] == abc and blockchain.nfts[k]['metadata']['nft'] == '' and blockchain.nfts[k]['metadata']['status'] == 'no':
                        result += int(blockchain.nfts[k]['metadata']['how'])
                    elif k == token and blockchain.nfts[k]['owner'] == abc and blockchain.nfts[k]['metadata']['nft'] == '' and blockchain.nfts[k]['metadata']['status'] == 'sale':
                        result -= int(blockchain.nfts[k]['metadata']['how'])
            elif blockchain.chain[i].transactions[j]['type'] == 'transfer' and blockchain.chain[i].transactions[j]['from'] == abc:
                token = blockchain.chain[i].transactions[j]['token_id']
                for k in blockchain.nfts:
                    if k == token and blockchain.nfts[k]['metadata']['nft'] == '':
                        result -= int(blockchain.nfts[k]['metadata']['how'])
                    elif k == token and blockchain.nfts[k]['metadata']['nft'] != '':
                        result += int(blockchain.nfts[k]['metadata']['how'])
            elif blockchain.chain[i].transactions[j]['type'] == 'transfer' and blockchain.chain[i].transactions[j]['to'] == abc:
                token = blockchain.chain[i].transactions[j]['token_id']
                for k in blockchain.nfts:
                    if k == token and blockchain.nfts[k]['metadata']['nft'] == '':
                        result += int(blockchain.nfts[k]['metadata']['how'])
                    elif k == token and blockchain.nfts[k]['metadata']['nft'] != '':
                        result -= int(blockchain.nfts[k]['metadata']['how'])
    if result < int(new['how']):
        return 'Low money', 400
    token = randint(1, 10*10000000000)
    blockchain.mint_nft(new['id_seller'], token, {'how': new['how'], 'nft': '', 'sum': 0, 'number': '', 'status': 'sale', 'creator': 'friends2.0'})
    blockchain.transfer_nft(new['id_seller'], str(reciever), token)'''

    #эмитатор
    cursor.execute('SELECT * FROM balances')
    records = cursor.fetchall()
    for row in records:
        if str(row[0]) == new['id_seller']:
            balance_seller = row[1]
        elif row[0] == reciever:
            balance_receiver = row[1]
    if balance_seller < int(new['how']):
        return 'Low money', 400
    cursor.execute('UPDATE balances SET balance = ? WHERE hash = ?', (balance_seller - int(new['how']), new['id_seller']))
    cursor.execute('UPDATE balances SET balance = ? WHERE hash = ?', (balance_receiver + int(new['how']), reciever))
    con.commit()


    cursor.execute('INSERT INTO chats (autor_id, giver_id, text, file, read, special) VALUES (?, ?, ?, ?, ?, ?)', (author, new['id_giver'], ('Вам переведено ' + str(new['how'] + ' ICE')), '', 'no', 'ice'))
    con.commit()
    return jsonify({'answer': 'yes'})
@app.route('/buy_nft', methods = ['POST'])
def buy_nft():
    new = request.json
    '''blockchain.nfts[new['ip']]['metadata']['how'] = new['how']
    blockchain.nfts[new['ip']]['metadata']['status'] = 'sale'''

    #эмитатор
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM nfts')
    records = cursor.fetchall()
    for row in records:
        if row[0] == new['ip']:
            creator = row[2]
    cursor.execute('INSERT INTO preds (token, owner, creator, cost, sum, nft) VALUES (?, ?, ?, ?, ?, ?)', (float(new['ip']), float(new['hash']), creator, int(new['how']), 0, new['nft']))
    con.commit()


    return jsonify({'answer': 'yes'})
@app.route('/gift', methods = ['POST'])
def gift():
    new = request.json
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if row[4] == new['adress']:
            receiver = str(row[6])
        elif str(row[6]) == new['hash']:
            autor = row[4]
    '''blockchain.nfts[new['number']]['owner'] = receiver'''

    #эмитатор
    cursor.execute('UPDATE nfts SET owner = ? WHERE token = ?', (receiver, new['number']))
    cursor.execute('SELECT * FROM nfts')
    records = cursor.fetchall()
    for row in records:
        if row[0] == new['number']:
            nft = row[4]

    
    '''cursor.execute('INSERT INTO chats (autor_id, giver_id, text, file, read, special) VALUES (?, ?, ?, ?, ?, ?)', (autor, new['adress'], 'Вам подарен подарок!', blockchain.nfts[new['number']]['metadata']['nft'], 'no', 'nft'))'''

    #эмитатор
    cursor.execute('INSERT INTO chats (autor_id, giver_id, text, file, read, special) VALUES (?, ?, ?, ?, ?, ?)', (autor, new['adress'], 'Вам подарен подарок!', nft, 'no', 'nft'))

    
    con.commit()
    return jsonify({'answer': 'yes'})
@app.route('/bans', methods = ['POST'])
def bans():
    new = request.json
    con = sl.connect('exercises.db', check_same_thread = False)
    cursor = con.cursor()
    bans = 0
    cursor.execute('SELECT * FROM users')
    records = cursor.fetchall()
    for row in records:
        if row[4] == new['id']:
            bans = row[8]
    cursor.execute('UPDATE users SET bans = ? WHERE id = ?', (bans + 1, new['id']))
    cursor.execute('INSERT INTO chats (autor_id, giver_id, text, file, read, special) VALUES (?, ?, ?, ?, ?, ?)', ('Sophie', new['id'], 'На тебя подана жалоба. После рассмотрения это модераторами ты можешь быть заблокирован', '', 'no', 'bans'))
    con.commit()
    return jsonify({'OK': 200})
if __name__ == '__main__':
    app.run(debug = False, host = '0.0.0.0')
