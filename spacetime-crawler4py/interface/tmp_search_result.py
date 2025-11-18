def process_query(query):
    fake_results = []
    for i in range(5):
        fake_results.append({'url': query + "/" + str(i)})
    print(fake_results)
    return fake_results