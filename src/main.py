from .dataset_extractor.main import exec_process
import time


def main():
    search_queries = [
        'Lionel Messi',
        'Javier Milei',
        'Uala Argentina',
        'Agustin Laje',
        'Personal',
        'Netflix Argentina',
        'ICBC Argentina',
        'Jennifer Aniston',
        'Asesor',
        'Banco Santander',
        'Banco Galicia',
        'Banco Macro',
        'Banco BBVA',
        'Banco Hipotecario',
        'Banco Nacion',
        'Banco Ciudad',
        'Banco Patagonia',
        'Banco Supervielle',
        'Banco Comafi',
        'Banco Itau',
        'UADE',
        'UBA',
        'UTN',
        'UNLP',
        'UNLaM',
        'Google',
        'Amazon',
        'Apple',
        'Microsoft',
        'Facebook',
    ]

    while True:  # Bucle infinito
        for search_query in search_queries:
            index = 0
            print(f"Buscando datos para: {search_query}")
            exec_process(search_query, 100)

            if index + 1 <= len(search_queries):
                print("Esperando 1 minuto...")
                time.sleep(60)
                index += 1

        print("Scrapping finalizado.")
        break
    
    exit(0)


if __name__ == "__main__":
    main()
