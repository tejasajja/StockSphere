from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['stocksphere'] 


print("1) Customers with Most Stock Transactions \n")

limit = 10  


transactions = list(db.transactions.find())


for transaction in transactions:
    if transaction.get('crypto_id', 1) == 0:
        continue
    stocks = list(db.stocks.find({"Company_ticker": transaction["ticket"]}))
    if stocks:
        transaction["stock_info"] = stocks[0]  


for transaction in transactions:
    if transaction.get('crypto_id', 1) == 0:
        continue
    if "customer_id" in transaction:
        customers = list(db.customers.find({"customer_id": transaction["customer_id"]}))
        if customers:
            transaction["customer_info"] = customers[0]
    if "agent_id" in transaction:
        agents = list(db.agents.find({"agent_id": transaction["agent_id"]}))
        if agents:
            transaction["agent_info"] = agents[0]


from collections import defaultdict
grouped_data = defaultdict(lambda: {'total_transactions': 0, 'customer_info': None, 'agent_info': None})

for transaction in transactions:
    if transaction.get('crypto_id', 1) == 0:
        continue
    key = transaction["customer_id"]
    grouped_data[key]['total_transactions'] += 1
    if 'customer_info' in transaction:
        grouped_data[key]['customer_info'] = transaction['customer_info']
    if 'agent_info' in transaction:
        grouped_data[key]['agent_info'] = transaction['agent_info']


sorted_transactions = sorted(grouped_data.items(), key=lambda x: x[1]['total_transactions'], reverse=True)[:limit]


results = [{
    "customer_id": key,
    "username": val['customer_info']['username'] if val['customer_info'] else None,
    "email": val['customer_info']['email'] if val['customer_info'] else None,
    "total_transactions": val['total_transactions'],
    "agent_name": val['agent_info']['name'] if val['agent_info'] else None,
    "agent_level": val['agent_info']['level'] if val['agent_info'] else None
} for key, val in sorted_transactions]

for result in results:
    print(result)


###########

print("\n\n\n")

print("2) Agents with Top Stock Transactions \n")

limit = 10  

transactions = list(db.transactions.find())

for transaction in transactions:
    if transaction.get('crypto_id', 1) == 0:
        continue
    stocks = list(db.stocks.find({"Company_ticker": transaction["ticket"]}))
    if stocks:
        transaction["stock_info"] = stocks[0]

for transaction in transactions:
    if transaction.get('crypto_id', 1) == 0:
        continue
    if "agent_id" in transaction:
        agents = list(db.agents.find({"agent_id": transaction["agent_id"]}))
        if agents:
            transaction["agent_info"] = agents[0]

from collections import defaultdict
agent_totals = defaultdict(lambda: {'total_cost': 0, 'agent_info': None})

for transaction in transactions:
    if transaction.get('crypto_id', 1) == 0:
        continue
    agent_id = transaction.get("agent_id")
    if agent_id:
        volume = transaction.get("volume", 0)
        each_cost = transaction.get("each_cost", 0)
        action = transaction.get("action", "")
        multiplier = 1 if action == "buy" else -1
        total_cost_contribution = volume * each_cost * multiplier
        
        agent_totals[agent_id]['total_cost'] += total_cost_contribution
        if 'agent_info' in transaction:
            agent_totals[agent_id]['agent_info'] = transaction['agent_info']

sorted_agents = sorted(agent_totals.items(), key=lambda x: x[1]['total_cost'], reverse=True)[:limit]

results = [{
    "agent_id": agent_id,
    "agent_name": agent_info['agent_info']['name'] if agent_info['agent_info'] else None,
    "agent_level": agent_info['agent_info']['level'] if agent_info['agent_info'] else None,
    "total_cost": agent_info['total_cost']
} for agent_id, agent_info in sorted_agents]

for result in results:
    print(result)


##########

print("\n\n\n")

print("3) Customers with Top Stock Transactions \n")

transactions = list(db.transactions.find())
stocks_dict = {stock['Company_ticker']: stock for stock in db.stocks.find()}
customers_dict = {customer['customer_id']: customer for customer in db.customers.find()}
agents_dict = {agent['agent_id']: agent for agent in db.agents.find()}

customer_aggregates = {}

for transaction in transactions:
    
    if transaction.get('crypto_id', 1) == 0:
        continue
    
    stock_info = stocks_dict.get(transaction.get('ticket'))
    customer_info = customers_dict.get(transaction.get('customer_id'))
    agent_info = agents_dict.get(transaction.get('agent_id'))

    if customer_info and agent_info:
        customer_id = transaction['customer_id']
        if customer_id not in customer_aggregates:
            customer_aggregates[customer_id] = {
                'total_cost': 0,
                'customer_info': customer_info,
                'agent_info': agent_info
            }
        
        volume = transaction.get('volume', 0)
        each_cost = transaction.get('each_cost', 0)
        action_multiplier = 1 if transaction.get('action') == 'buy' else -1
        total_cost = volume * each_cost * action_multiplier

        customer_aggregates[customer_id]['total_cost'] += total_cost

sorted_customers = sorted(customer_aggregates.items(), key=lambda x: x[1]['total_cost'], reverse=True)[:limit]

results = [{
    'customer_id': cust_id,
    'username': cust['customer_info']['username'],
    'email': cust['customer_info']['email'],
    'total_cost': cust['total_cost'],
    'agent_name': cust['agent_info']['name'],
    'agent_level': cust['agent_info']['level']
} for cust_id, cust in sorted_customers]

for result in results:
    print(result)


#######

print("\n\n\n")

print("4) Customers with Top Crypto Transactions \n")

transactions = list(db.transactions.find())
crypto_dict = {crypto['Symbol']: crypto for crypto in db.cryptocurrencies.find()}
customers_dict = {customer['customer_id']: customer for customer in db.customers.find()}
agents_dict = {agent['agent_id']: agent for agent in db.agents.find()}


customer_aggregates = {}


for transaction in transactions:
    
    if transaction.get('stock_id', 1) == 0:
        continue
    
    crypto_info = crypto_dict.get(transaction.get('ticket'))
   
    customer_info = customers_dict.get(transaction.get('customer_id'))
    
    agent_info = agents_dict.get(transaction.get('agent_id'))
    if customer_info and agent_info:
        customer_id = transaction['customer_id']
        if customer_id not in customer_aggregates:
            customer_aggregates[customer_id] = {
                'total_cost': 0,
                'customer_info': customer_info,
                'agent_info': agent_info
            }
        
        
        volume = transaction.get('volume', 0)
        each_cost = transaction.get('each_cost', 0)
        action_multiplier = 1 if transaction.get('action') == 'buy' else -1
        total_cost = volume * each_cost * action_multiplier

        
        customer_aggregates[customer_id]['total_cost'] += total_cost

sorted_customers = sorted(customer_aggregates.items(), key=lambda x: x[1]['total_cost'], reverse=True)[:limit]




results = [{
    'customer_id': cust_id,
    'username': cust['customer_info']['username'],
    'email': cust['customer_info']['email'],
    'total_cost': cust['total_cost'],
    'agent_name': cust['agent_info']['name'],
    'agent_level': cust['agent_info']['level']
} for cust_id, cust in sorted_customers]

for result in results:
    print(result)




print("\n\n\n")

print("5) Agents with Top Crypto Transactions \n")

limit = 10


transactions = list(db.transactions.find())


for transaction in transactions:
    
    if transaction.get('stock_id', 1) == 0:
        continue
    
    cryptos = list(db.cryptocurrencies.find({"Symbol": transaction["ticket"]}))
    if cryptos:
        transaction["crypto_info"] = cryptos[0] 


for transaction in transactions:
    if transaction.get('stock_id', 1) == 0:
        continue
    if "agent_id" in transaction:
        agents = list(db.agents.find({"agent_id": transaction["agent_id"]}))
        if agents:
            transaction["agent_info"] = agents[0]


agent_totals = defaultdict(lambda: {'total_cost': 0, 'agent_info': None})


for transaction in transactions:
    if transaction.get('stock_id', 1) == 0:
        continue
    agent_id = transaction.get("agent_id")
    if agent_id:
        volume = transaction.get("volume", 0)
        each_cost = transaction.get("each_cost", 0)
        action = transaction.get("action", "")
        multiplier = 1 if action == "buy" else -1  
        total_cost_contribution = volume * each_cost * multiplier
        
        agent_totals[agent_id]['total_cost'] += total_cost_contribution
        if 'agent_info' in transaction:
            agent_totals[agent_id]['agent_info'] = transaction['agent_info']


sorted_agents = sorted(agent_totals.items(), key=lambda x: x[1]['total_cost'], reverse=True)[:limit]


results = [{
    "agent_id": agent_id,
    "agent_name": agent_info['agent_info']['name'] if agent_info['agent_info'] else None,
    "agent_level": agent_info['agent_info']['level'] if agent_info['agent_info'] else None,
    "total_cost": agent_info['total_cost']
} for agent_id, agent_info in sorted_agents]


for result in results:
    print(result)
    
######

print("\n\n\n")

print("6) Customers with Most Cryptocurrency Transactions \n")

limit = 10  

transactions = list(db.transactions.find())

for transaction in transactions:
    if transaction.get('stock_id', 1) == 0:
        continue
    cryptos = list(db.cryptocurrencies.find({"Symbol": transaction["ticket"]}))
    if cryptos:
        transaction["crypto_info"] = cryptos[0]  


for transaction in transactions:
    if transaction.get('stock_id', 1) == 0:
        continue
    if "customer_id" in transaction:
        customers = list(db.customers.find({"customer_id": transaction["customer_id"]}))
        if customers:
            transaction["customer_info"] = customers[0]
    if "agent_id" in transaction:
        agents = list(db.agents.find({"agent_id": transaction["agent_id"]}))
        if agents:
            transaction["agent_info"] = agents[0]


grouped_data = defaultdict(lambda: {'total_transactions': 0, 'customer_info': None, 'agent_info': None})

for transaction in transactions:
    if transaction.get('stock_id', 1) == 0:
        continue
    key = transaction["customer_id"]
    grouped_data[key]['total_transactions'] += 1
    if 'customer_info' in transaction:
        grouped_data[key]['customer_info'] = transaction['customer_info']
    if 'agent_info' in transaction:
        grouped_data[key]['agent_info'] = transaction['agent_info']


sorted_transactions = sorted(grouped_data.items(), key=lambda x: x[1]['total_transactions'], reverse=True)[:limit]

results = [{
    "customer_id": key,
    "username": val['customer_info']['username'] if val['customer_info'] else None,
    "email": val['customer_info']['email'] if val['customer_info'] else None,
    "total_transactions": val['total_transactions'],
    "agent_name": val['agent_info']['name'] if val['agent_info'] else None,
    "agent_level": val['agent_info']['level'] if val['agent_info'] else None
} for key, val in sorted_transactions]

for result in results:
    print(result)