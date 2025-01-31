from src.models.hospital import Hospital
import threading
import time
from src.utils.logger import get_logger
import src.config as config


logger = get_logger(__name__)



def take_snapshot(hospital: Hospital):
    while True:
        hospital.take_snapshot()
        time.sleep(config.SNAPSHOT_CLOCK_INTERVAL / hospital.time_rate)

def admit_patient(hospital: Hospital):
    while True:
        hospital.admit_patient()
        time.sleep(config.ADMIT_PATIENT_CLOCK_INTERVAL / hospital.time_rate)


if __name__ == "__main__":
    logger.info("application started")
    hospital = Hospital("hospital", 15, config.WORLDMODEL_BASE_URL)

    try:
        hospital.register()
        
        snapshot_thread = threading.Thread(
            target=take_snapshot, args=(hospital,)
        )
        snapshot_thread.daemon = True
        snapshot_thread.start()
        
        admit_thread = threading.Thread(
            target=admit_patient, args=(hospital,)
        )
        admit_thread.daemon = True
        admit_thread.start()
        
        while True:
            pass

    except KeyboardInterrupt:
        print(f"In {__name__}: Program interrupted by user. Shutting down...")
    except Exception as error:
        print(f"In {__name__}:\n" + f"Unexpected error: {error}")
