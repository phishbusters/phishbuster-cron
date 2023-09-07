from .dataset_extractor.main import exec_process
import time

def main():
    search_queries = ['Uala Argentina', 'Javier Milei'] 
    
    while True:  # Bucle infinito
        for search_query in search_queries:
            index = 0
            print(f"Buscando datos para: {search_query}")
            exec_process(search_query, 10)

            if index + 1 <= len(search_queries):
                print("Esperando 5 minutos...")
                time.sleep(300)
                index += 1

        print("Scrapping finalizado.")
        break


if __name__ == "__main__":
    main()
