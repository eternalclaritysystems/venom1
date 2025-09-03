import importlib

def run_ingestor(module_name: str):
    """
    Dynamically imports and runs the ingest_data function
    from a given ingestion module.
    """
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, "ingest_data"):
            print(f"[+] Running {module_name}...")
            data = module.ingest_data()
            # Here you could insert 'data' into your database
            return data
        else:
            print(f"[!] Module {module_name} does not have ingest_data()")
            return None
    except Exception as e:
        print(f"[!] Error running {module_name}: {e}")
        return None

if __name__ == "__main__":
    ingestion_modules = [
        "v_cde_ticketmaster",
        "v_cde_arcgis",
    ]

    for mod in ingestion_modules:
        run_ingestor(mod)
