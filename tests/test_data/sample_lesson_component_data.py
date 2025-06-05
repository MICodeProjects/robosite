"""Sample lesson component data for testing"""

SAMPLE_lesson_componentS = [
    {
        "name": "Introduction Text",
        "id": 1,
        "lesson_id": 1,
        "type": 1,  # Text
        "content": "{\"text\": \"Welcome to robotics! This lesson covers...\"}"
    },
    {
        "name": "Python Variables",
        "id": 2,
        "lesson_id": 2,
        "type": 2,  # Video
        "content": "{\"url\": \"https://example.com/video1\"}"
    },
    {
        "name": "Sensor Quiz",
        "id": 3,
        "lesson_id": 3,
        "type": 3,  # Quiz
        "content": "{\"questions\": [{\"q\": \"What is a sensor?\", \"options\": [\"A\", \"B\", \"C\"], \"correct\": 0}]}"
    },
    {
        "name": "CAD Exercise",
        "id": 4,
        "lesson_id": 4,
        "type": 4,  # Exercise
        "content": "{\"instructions\": \"Create a simple cube in CAD...\"}"
    },
    {
        "name": "PID Simulator",
        "id": 5,
        "lesson_id": 5,
        "type": 5,  # Interactive
        "content": "{\"simulator_config\": {\"setpoint\": 100, \"kp\": 1, \"ki\": 0.1, \"kd\": 0.01}}"
    }
]