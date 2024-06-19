from services.llamager import LLamager



llm = LLamager()

while True: 

    question = input("user: ")
    response = llm.process(question, 'user', '123')
    