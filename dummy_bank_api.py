from flask import Flask, request, jsonify

app = Flask(__name__)

# Sample data for bank accounts with additional details
accounts = {
    'KAVITA': {
        'name': 'Kavita',
        'balance': 2500.00,
        'currency': 'USD',
        'address': '123 Maple Street, Springfield',
        'phone': '555-1234',
        'email': 'alice@example.com',
        'pin': '1111',
        'allowed_accounts': {
            'SUSAN': 'Susan',
            'ARJUN': 'Arjun'
        },
        'EMI': {
            'amount': 1500.00,
            'due_date': '2024-07-30'  # Example due date for Kavita's EMI
        }
    },
    'SUSAN': {
        'name': 'Susan',
        'balance': 5400.75,
        'currency': 'USD',
        'address': '456 Oak Avenue, Springfield',
        'phone': '555-5678',
        'email': 'bob@example.com',
        'pin': '2222',
        'allowed_accounts': {
            'ARJUN': 'Arjun'
        },
        'EMI': {
            'amount': 1200.00,
            'due_date': '2024-07-25'  # Example due date for Susan's EMI
        }
    },
    'ARJUN': {
        'name': 'Arjun',
        'balance': 320.40,
        'currency': 'USD',
        'address': '789 Pine Road, Springfield',
        'phone': '555-9012',
        'email': 'charlie@example.com',
        'pin': '3333',
        'allowed_accounts': {
            'KAVITA': 'Kavita',
            'SUSAN' : 'Susan'

        },
        'EMI': {
            'amount': 800.00,
            'due_date': '2024-07-28'  # Example due date for Arjun's EMI
        }
    },
    'EMI':{
        'name':'BANK',
        'balance':10000,
        'currency':'USD'
        }
}


@app.route('/api/account/<account_number>', methods=['GET'])
def get_account(account_number):
    account = accounts.get(account_number)
    if account:
        
        return jsonify(account)
    else:
        return jsonify({'error': 'Account not found'}), 404

@app.route('/api/transfer', methods=['POST'])
def transfer():
    data = request.get_json()

    source_account = data.get('source_account')
    destination_account = data.get('destination_account')
    amount = data.get('amount')
    pin = data.get('pin')

    if not source_account or not destination_account or not amount or not pin:
        return jsonify({'error': 'Missing required fields'}), 400

    source = accounts.get(source_account)
    destination = accounts.get(destination_account)

    if not source:
        return jsonify({'error': f'Source account {source_account} not found'}), 404
    if not destination:
        return jsonify({'error': f'Destination account {destination_account} not found'}), 404
    if source['pin'] != pin:
        return jsonify({'error': 'Invalid PIN'}), 401
    if destination_account not in source['allowed_accounts']:
        return jsonify({'error': 'Destination account not allowed'}), 403
    if source['balance'] < amount:
        return jsonify({'error': 'Insufficient funds in source account'}), 400

    source['balance'] -= amount
    destination['balance'] += amount

    return jsonify({
        'message': 'Transfer successful',
        'source_account_balance': source['balance'],
        'destination_account_balance': destination['balance']
    })

@app.route('/api/accounts/<source_account>', methods=['GET'])
def list_accounts(source_account):
    source = accounts.get(source_account)
    if not source:
        return jsonify({'error': f'Source account {source_account} not found'}), 404

    allowed_accounts = [{'account_number': acc_number, 'name': name}
                        for acc_number, name in source['allowed_accounts'].items()]
    return jsonify(allowed_accounts)




@app.route('/api/pay_emi', methods=['POST'])
def pay_emi():
    data = request.get_json()

    account_number = data.get('account_number')
    pin = data.get('pin')

    if not account_number or not pin:
        return jsonify({'error': 'Missing required fields'}), 400

    account = accounts.get(account_number)
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    if account['pin'] != pin:
        return jsonify({'error': 'Invalid PIN'}), 401

    emi_details = account.get('EMI')
    if not emi_details:
        return jsonify({'error': 'No EMI details found for this account'}), 404

    emi_amount = emi_details['amount']
    if account['balance'] < emi_amount:
        return jsonify({'error': 'Insufficient funds to pay EMI'}), 400

    account['balance'] -= emi_amount
    emi_account = accounts.get('EMI')
    emi_account['balance'] += emi_amount
    account['EMI']=None


    return jsonify({
        'message': 'EMI payment successful',
        'remaining_balance': account['balance'],
        'emi_account_balance': emi_account['balance']
    })

if __name__ == '__main__':
    app.run(debug=True , port=6000)

