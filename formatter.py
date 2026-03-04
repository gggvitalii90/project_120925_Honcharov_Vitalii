try:
    from tabulate import tabulate
except Exception:
    tabulate = None

def pretty_print_results(results):
    if not results:
        print('No results')
        return
    if tabulate:
        headers = list(results[0].keys())
        rows = [[r.get(h, '') for h in headers] for r in results]
        print(tabulate(rows, headers=headers, tablefmt='grid'))
    else:
        for r in results:
            print('---')
            for k, v in r.items():
                print(f'{k}: {v}')
