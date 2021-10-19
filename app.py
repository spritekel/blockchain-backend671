#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  6 00:55:36 2021

@author: sprite
"""

# Creating the blockchain

import datetime
import hashlib
import json
from flask import Flask, jsonify
from flask.wrappers import Request
from flask import request
import qrcode
from PIL import Image
import base64
import pymongo
import bcrypt


# development

# Part 1 - build the blockchain

class Blockchain:
    # needed componenets genesisblock, chain, createblock, checks

    def __init__(self):
        self.chain = []
        self.create_block(proof=1, prev_Hash='0', hashcode='0', imgQRcode=0)

    def create_block(self, proof, prev_Hash, hashcode, imgQRcode):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'prev_hash': prev_Hash,
            'Data': hashcode,
            'NftRawQR': imgQRcode
        }
        self.chain.append(block)
        return block

    def get_prev_block(self):
        return self.chain[-1]

    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False

        while check_proof is False:
            # this will determine the difficulty of mining(**2 make it harder but still easy)
            hash_operation = hashlib.sha256(
                str(new_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        prev_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['prev_hash'] != self.hash(prev_block):
                return False
            prev_proof = prev_block['proof']
            proof = block['proof']

            # must be the same as the proofofwork
            hash_operation = hashlib.sha256(
                str(proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            prev_block = block
            block_index += 1
        return True
    
    def exists_in_chain(self, chain, checkHash):
        #prev_block = chain[0]
        
        block_index = 0
        while block_index < len(chain):
            block = chain[block_index]
            if block['Data'] == checkHash:
                return True
            block_index += 1
        return False
                
    def createNFTQRcode(self):
        logo_link = 'Hermes.png'
        logo = Image.open(logo_link)
        basewidth = 100
        wpercent = (basewidth/float(logo.size[0]))
        hsize = int((float(logo.size[1])*float(wpercent)))
        logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
        QRcode = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_H
        )
        url = 'https://www.google.com'
        QRcode.add_data(url)
        QRcode.make()
        QRcolor = 'Black'
        QRimg = QRcode.make_image(
            fill_color=QRcolor, back_color="white").convert('RGB')
        pos = ((QRimg.size[0] - logo.size[0]) // 2,
        (QRimg.size[1] - logo.size[1]) // 2)
        QRimg.paste(logo, pos)
        QRimg.save('NFT_QR_Image.png')
        print("QR image generated!! :D")
        with open("NFT_QR_Image.png", "rb") as imageFile:
            imageString = base64.b64encode(imageFile.read())
        return imageString.decode('utf-8')  
    


# Part 2 - Mining our blockchain
# Create a web app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.secret_key = "Kel123pop!"
client = pymongo.MongoClient("mongodb+srv://testuser:<password>@itri671project.h5egg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.get_database('total_records')
records = db.register

# Create a blockchain
blockchain = Blockchain()


@app.route('/hashValidate', methods=['POST'])
def hashValidate():
    hashcode = request.args.get('hashcode')
    #hashcode = blockchain.hash(hashcode)
    print(hashcode)
    
    prev_block = blockchain.get_prev_block()
    prev_proof = prev_block['proof']
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)

    testHash = b"Kelvin"
    #testHash = json.dumps(testHash).encode()
    testHash = hashlib.sha256(testHash).hexdigest()
    imgRawData = blockchain.createNFTQRcode()
    block = blockchain.create_block(proof, prev_hash, hashcode, imgRawData)
    response = {'message': 'Congradulations, successfully mined a block',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'prev_hash': block['prev_hash'],
                'TestHash': hashcode,
                'QR': block['NftRawQR']}
    print(jsonify(response))
    return jsonify(response), 200


# mining a new block
# @app.route('/mine_block', methods = ['GET'])
def mine_block(hashcode):
    prev_block = blockchain.get_prev_block()
    prev_proof = prev_block['proof']
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)

    testHash = b"Kelvin"
    #testHash = json.dumps(testHash).encode()
    testHash = hashlib.sha256(testHash).hexdigest()
    block = blockchain.create_block(proof, prev_hash)
    response = {'message': 'Congradulations, successfully mined a block',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'prev_hash': block['prev_hash'],
                'TestHash': hashcode}
    print(jsonify(response))
    return jsonify(response), 200

# getting the full blockchain
@app.route('/get_chain', methods={'GET'})
def get_chain():
    response = {'blockchain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

#Checking if the chain is valid!!
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'Blockchain is valid'}
    else:
        response = {'message': 'Blockchain is not valid!!! :('}
    return jsonify(response), 200

@app.route('/search_chain', methods = ['POST'])
def search_chain():
    hashcode = request.args.get('hashcode')
    #print(hashcode)
    is_valid = blockchain.exists_in_chain(blockchain.chain, hashcode)
    if is_valid:
        response = {'message': 'Exists'}
    else:
        response = {'message': 'Does not exist'}
    return jsonify(response), 200
    
@app.route('/login', methods = ['POST'])
def login():
    user = request.args.get('username')
    password1 = request.args.get('password')

    print(user + " : " + password1)
    pass
    
    

# Functions to run the application
app.run(host='0.0.0.0', port=5000)
