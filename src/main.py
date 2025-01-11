from src.models.hospital import Hospital
import threading
import time


def register(api_url: str, hospital: Hospital):
    registered = hospital.register(api_url + "/register")
    print(f"In {__name__}.{register.__name__}: register called")
    print(100 * "-")

    if registered:
        print(f'In {__name__}.{register.__name__}: Registered with Success!')
        print(100 * "-")
        return True

    print(f'In {__name__}.{register.__name__}: Registration Failed!')
    print(100 * "-")
    return False


def take_snapshot(url, hospital: Hospital):
    while True:
        if hospital.get_entity_id():
            try:
                hospital.take_snapshot(url + f"/snapshot")
                print(f"In {__name__}.{take_snapshot.__name__}: take_snapshot called")
                print(100 * "-")
            except Exception as error:
                print(f"In {__name__}.{take_snapshot.__name__}:\n" +
                      f"Error: {error}")
                print(100 * "-")
        time.sleep(10)


def admit_patient(admit_url: str, discharge_url: str, hospital: Hospital):
    while True:
        if hospital.get_entity_id():
            try:
                hospital.admit_patient(admit_url, discharge_url)
                print(f"In {__name__}.{admit_patient.__name__}: admit_patient called")
                print(100 * "-")
            except Exception as error:
                print(f"In {__name__}.{admit_patient.__name__}:\n" +
                      f"Error: {error}")
                print(100 * "-")
        time.sleep(10)


if __name__ == "__main__":
    url = 'http://localhost:8000/api'
    hospital = Hospital('hospital', 15)

    while not register(url, hospital):
        print(f"In main.{__name__}: Trying again in 5 seconds")
        print(100 * "-")
        time.sleep(5)
        register(url, hospital)

    try:
        # Starting the Snapshot Thread
        threading.Thread(target=take_snapshot, args=(url, hospital)).start()
        threading.Thread(target=admit_patient, args=(url + f"/accept-person", url+f"/service-done", hospital)).start()

    except KeyboardInterrupt:
        print(f"In {__name__}: Program interrupted by user. Shutting down...")
    except Exception as error:
        print(f"In {__name__}:\n" +
              f"Unexpected error: {error}")
