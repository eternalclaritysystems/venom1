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
            module.ingest_data()
        else:
            print(f"[!] Module {module_name} does not have ingest_data()")
    except Exception as e:
        print(f"[!] Error running {module_name}: {e}")


if __name__ == "__main__":
    # List of ingestion modules to activate
    ingestion_modules = [
        "v_cde_ticketmaster",   # ticketmaster ingestion
        # "v_cde_twitter",    # Example: Twitter ingestion
        # "v_cde_rtsp",       # Example: RTSP ingestion
    ]

    for module_name in ingestion_modules:
        run_ingestor(module_name)
