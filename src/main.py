from src.models.hospital import Hospital
import threading
import time
from src.utils.logger import get_logger


logger = get_logger(__name__)

global_stop_event = threading.Event()


def take_snapshot(hospital: Hospital, stop_event: threading.Event):
    while not stop_event.is_set():
        hospital.take_snapshot()
        time.sleep(4)

def admit_patient(hospital: Hospital, stop_event: threading.Event):
    while not stop_event.is_set():
        hospital.admit_patient()
        time.sleep(2)


# def admit_patient(admit_url: str, discharge_url: str, hospital: Hospital):
#     while True:
#         if hospital.get_entity_id():
#             try:
#                 hospital.admit_patient(admit_url, discharge_url)
#                 print(f"In {__name__}.{admit_patient.__name__}: admit_patient called")
#                 print(100 * "-")
#             except Exception as error:
#                 print(f"In {__name__}.{admit_patient.__name__}:\n" + f"Error: {error}")
#                 print(100 * "-")
#         time.sleep(10)


if __name__ == "__main__":
    logger.info("application started")
    url = "http://localhost:8000/api"
    hospital = Hospital("hospital", 15, url)

    # while not register(url, hospital):
    #     print(f"In main.{__name__}: Trying again in 5 seconds")
    #     print(100 * "-")
    #     time.sleep(5)
    #     register(url, hospital)

    try:
        hospital.register()
        
        snapshot_thread = threading.Thread(
            target=take_snapshot, args=(hospital, global_stop_event)
        )
        snapshot_thread.start()
        
        admit_thread = threading.Thread(
            target=admit_patient, args=(hospital, global_stop_event)
        )
        admit_thread.start()
        # threading.Thread(
        #     target=admit_patient,
        #     args=(url + f"/accept-person", url + f"/service-done", hospital),
        # ).start()

    except KeyboardInterrupt:
        global_stop_event.set()
        print(f"In {__name__}: Program interrupted by user. Shutting down...")
    except Exception as error:
        print(f"In {__name__}:\n" + f"Unexpected error: {error}")
