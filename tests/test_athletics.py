from fastapi.testclient import TestClient
import server


client = TestClient(server.app)


def sample_payload():
    return {
        'shoulder_soreness': 1,
        'elbow_soreness': 1,
        'forearm_tightness': 1,
        'triceps_fatigue': 1,
        'biceps_pain': 1,
        'shoulder_clicking': 0,
        'pitches_today': 50,
        'pitches_7d': 200,
        'velocity_drop': 0,
        'arm_slot_change': 0,
        'command_loss': 0,
        'effort_level': 5,
        'follow_through_pain': 0,
        'sleep_hours': 8.0,
        'recovery_quality': 8,
        'hydration_level': 8,
        'nutrition_quality': 8,
        'soreness_recovery': 8,
        'rest_days': 2,
        'stress_level': 3,
        'motivation_level': 8,
        'concentration_score': 8,
        'mood_level': 8,
        'hip_flexor_tightness': 2,
        'quad_soreness': 2,
        'hamstring_tightness': 2,
        'glute_activation': 8,
        'calf_soreness': 1,
        'ankle_stability': 8,
        'knee_pain': 0,
        'groin_tightness': 0,
        'push_off_cramps': 0,
        'balance_stability': 8,
    }


def test_athletics_risk_happy_path():
    resp = client.post('/athletics/risk', json=sample_payload())
    assert resp.status_code == 200
    body = resp.json()
    assert body.get('status') == 'ok'
    assert 'risk_score' in body
    assert 'feedback' in body
