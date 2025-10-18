# app_athletics.py
# PredictWell Health.ai — Athletics Risk Endpoint (Pitcher AI with Sports Medicine Education)

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/athletics", tags=["Athletics"])

# ======== Input Schema ========
class PitcherIntake(BaseModel):
    # Section 1: Arm & Shoulder Condition
    shoulder_soreness: int
    inner_elbow_pain: int
    forearm_tightness: int
    triceps_fatigue: int
    biceps_pain: int
    shoulder_clicking: int

    # Section 2: Throwing Workload & Mechanics
    pitches_today: int
    pitches_7d: int
    velocity_drop: int
    arm_slot_change: int
    command_loss: int
    effort_level: int
    follow_through_pain: int

    # Section 3: Recovery & Readiness
    sleep_hours: float
    recovery_quality: int
    hydration_level: int
    nutrition_quality: int
    soreness_recovery: int
    rest_days: int

    # Section 4: Focus & Stress
    stress_level: int
    motivation_level: int
    concentration_score: int
    mood_level: int

    # Section 5: Lower-Body Health
    hip_flexor_tightness: int
    quad_soreness: int
    hamstring_tightness: int
    glute_activation: int
    calf_soreness: int
    ankle_stability: int
    knee_pain: int
    groin_tightness: int
    push_off_cramps: int
    balance_stability: int

# ======== Scoring Logic ========
def weighted_score(data: PitcherIntake) -> dict:
    """Computes weighted fatigue and overuse indicators by body region."""
    arm_load = (
        data.shoulder_soreness + data.inner_elbow_pain + data.forearm_tightness +
        data.triceps_fatigue + data.biceps_pain + data.shoulder_clicking
    ) / 6

    workload = (
        data.pitches_today / 100 +
        data.pitches_7d / 300 +
        data.velocity_drop / 5 +
        data.arm_slot_change / 5 +
        data.command_loss / 5 +
        data.effort_level / 5 +
        data.follow_through_pain / 5
    ) * 10

    recovery = (
        (10 - data.recovery_quality) +
        (10 - data.hydration_level) +
        (10 - data.nutrition_quality) +
        (10 - data.soreness_recovery)
    ) / 4

    mental = (
        data.stress_level +
        (10 - data.motivation_level) +
        (10 - data.concentration_score) +
        (10 - data.mood_level)
    ) / 4

    lower_body = (
        data.hip_flexor_tightness + data.quad_soreness + data.hamstring_tightness +
        data.glute_activation + data.calf_soreness + data.ankle_stability +
        data.knee_pain + data.groin_tightness + data.push_off_cramps + data.balance_stability
    ) / 10

    total_risk = (
        arm_load * 0.35 +
        workload * 0.25 +
        recovery * 0.15 +
        mental * 0.1 +
        lower_body * 0.15
    )

    return {
        "arm_load": round(arm_load, 2),
        "workload": round(workload, 2),
        "recovery": round(recovery, 2),
        "mental": round(mental, 2),
        "lower_body": round(lower_body, 2),
        "total_risk": round(total_risk, 2)
    }

# ======== EDUCATED AI: Sports Medicine Knowledge Base ========
def generate_feedback(scores: dict, data: PitcherIntake) -> str:
    """Creates evidence-based feedback using real sports medicine research."""
    lines = []
    
    # ===== LEVEL 1: URGENT (5/5) - IMMEDIATE MEDICAL ATTENTION =====
    urgent_alerts = []
    
    if data.inner_elbow_pain == 5:
        urgent_alerts.append(
            "⚠️ URGENT - Inner Elbow Pain (5/5): This is the PRIMARY indicator of UCL injury (Tommy John). "
            "You may experience instability, sharp pain on the inside of your elbow, and possible tingling in your ring/pinky fingers. "
            "STOP ALL THROWING immediately and schedule a sports medicine evaluation within 24-48 hours. "
            "UCL tears cannot heal on their own and early diagnosis is critical."
        )
    
    if data.shoulder_soreness == 5:
        urgent_alerts.append(
            "⚠️ URGENT - Shoulder Soreness (5/5): Maxed-out shoulder pain indicates potential rotator cuff tear or severe tendinitis. "
            "Pain at this level, especially if radiating to your arm or worsening at night, requires immediate evaluation. "
            "STOP THROWING for at least 3-5 days and see a sports medicine doctor. Continuing to throw risks career-ending injury."
        )
    
    if data.biceps_pain == 5:
        urgent_alerts.append(
            "⚠️ URGENT - Biceps Pain (5/5): Severe biceps pain can indicate labrum issues (SLAP tear) or biceps tendon damage. "
            "STOP THROWING and get evaluated - these injuries worsen rapidly without treatment."
        )
    
    if data.shoulder_clicking == 5:
        urgent_alerts.append(
            "⚠️ URGENT - Shoulder Clicking (5/5): Severe clicking/popping indicates structural damage to rotator cuff or labrum. "
            "This is NOT normal. Get evaluated before throwing again - you may have a tear that requires surgical repair."
        )
    
    # ===== LEVEL 2: RED FLAG (4/5) - SHUT DOWN 2-3 DAYS =====
    red_flags = []
    
    if data.inner_elbow_pain == 4:
        red_flags.append(
            "🚨 RED FLAG - Inner Elbow Pain (4/5): You're in the danger zone for Tommy John injury. "
            "NO THROWING for 2-3 days minimum. Inner elbow pain at this level means your UCL is under extreme stress. "
            "If pain persists after rest, see a doctor immediately."
        )
    
    if data.shoulder_soreness == 4:
        red_flags.append(
            "🚨 RED FLAG - Shoulder Soreness (4/5): Your rotator cuff is severely fatigued or inflamed. "
            "SHUT DOWN for 2-3 days - no throwing of any kind. Focus on rest, light stretching, and heat therapy (NOT ice). "
            "If you throw through this, you risk a tear that requires surgery."
        )
    
    if data.biceps_pain == 4:
        red_flags.append(
            "🚨 RED FLAG - Biceps Pain (4/5): High biceps pain suggests labrum stress or tendon inflammation. "
            "Take 2-3 days completely off from throwing. Continue with this pain and you risk a SLAP tear."
        )
    
    if data.shoulder_clicking >= 4:
        red_flags.append(
            "🚨 RED FLAG - Shoulder Clicking (4/5): Frequent clicking indicates joint instability or cartilage damage. "
            "Shut down for 2-3 days and get evaluated if clicking continues."
        )
    
    if data.forearm_tightness >= 4:
        red_flags.append(
            "🚨 RED FLAG - Forearm Tightness (4/5): Severe forearm tightness often precedes elbow injuries. "
            "Take 2 days off and focus on forearm stretching and heat therapy."
        )
    
    if data.follow_through_pain >= 4:
        red_flags.append(
            "🚨 RED FLAG - Follow-Through Pain (4/5): Pain during follow-through indicates shoulder or elbow stress at peak forces. "
            "This is a warning sign of impending injury. Rest 2-3 days immediately."
        )
    
    # Check workload violations
    if data.pitches_today > 105:
        red_flags.append(
            f"🚨 RED FLAG - Pitch Count ({data.pitches_today} today): You've exceeded safe limits (max 105 for 17-18 year olds). "
            "Overuse is the #1 cause of Tommy John injuries. STOP PITCHING and rest at least 4 days."
        )
    
    if data.pitches_7d > 300:
        red_flags.append(
            f"🚨 RED FLAG - Weekly Pitch Count ({data.pitches_7d} this week): You've thrown {data.pitches_7d} pitches in 7 days. "
            "Research shows this dramatically increases injury risk. Take 3-4 days off immediately."
        )
    
    # ===== Display Critical Alerts =====
    if urgent_alerts:
        lines.append("🚨 IMMEDIATE MEDICAL ATTENTION REQUIRED\n" + "\n\n".join(urgent_alerts))
    
    if red_flags:
        lines.append("⚠️ SHUT DOWN PROTOCOL - 2-3 Days Mandatory Rest\n" + "\n\n".join(red_flags))
    
    # ===== RECOVERY PROTOCOL (Evidence-Based) =====
    recovery_advice = []
    
    # Modern recovery science: NO ICE for normal soreness
    if any([data.shoulder_soreness >= 3, data.inner_elbow_pain >= 3, data.forearm_tightness >= 3]):
        recovery_advice.append(
            "Recovery Protocol\n"
            "• DO NOT ICE unless you have acute injury with sharp pain. Modern research shows icing DELAYS recovery by restricting blood flow.\n"
            "• DO USE HEAT: Apply heat for 20-30 minutes to promote blood flow and healing.\n"
            "• ACTIVE RECOVERY: Light cardio (stationary bike 10-15 min) and gentle arm circles increase nutrient-rich blood flow.\n"
            "• AVOID long-distance running - research shows it zaps power without aiding recovery.\n"
            "• HYDRATION: Drink extra water to help flush metabolic waste from muscles."
        )
    else:
        recovery_advice.append(
            "Recovery Looking Good\n"
            "Your arm metrics are in healthy range. Continue your current routine:\n"
            "• Maintain regular stretching and mobility work\n"
            "• Use heat therapy before throwing to warm tissues\n"
            "• Stay hydrated and get 7-9 hours of sleep\n"
            "• Keep workload below safe pitch count limits"
        )
    
    lines.extend(recovery_advice)
    
# Add this section to your generate_feedback() function
# Insert after the RECOVERY PROTOCOL section and before ARM HEALTH EDUCATION

    # ===== MUSCLE SORENESS EDUCATION (Personalized Based on Intake) =====
    muscle_education = []
    
    # ROTATOR CUFF SORENESS
    if data.shoulder_soreness >= 3:
        muscle_education.append(
            "💪 SHOULDER SORENESS - What's Happening & How to Recover\n\n"
            "Your Rotator Cuff Muscles (Most Likely Sore):\n"
            "• Infraspinatus & Teres Minor: These external rotators work ECCENTRICALLY during deceleration, "
            "experiencing extreme stress as they rapidly slow your arm down after ball release\n"
            "• Supraspinatus: Initiates arm elevation and gets compressed under your shoulder blade during cocking\n"
            "• Subscapularis: Works hard during internal rotation in the acceleration phase\n\n"
            
            "Why They're Sore:\n"
            "Your rotator cuff experiences supraphysiologic loads (forces beyond normal capacity) during throwing. "
            "The deceleration phase is particularly brutal - these small muscles must absorb massive forces to stop your arm. "
            "When you increase throwing volume too quickly or throw fatigued, you get microtrauma and inflammation at the tendon attachment points.\n\n"
            
            "RECOVERY PROTOCOL:\n"
            "✓ DO NOT ICE - Ice restricts blood flow and delays healing. Your inflammation is actually helping you rebuild stronger.\n"
            "✓ USE HEAT: 20-30 minutes before throwing to increase blood flow\n"
            "✓ Cross-Body Stretch: Proven most effective for restoring internal rotation. Hold 30 seconds x 3 reps\n"
            "✓ Sleeper Stretch: Lie on your side with arm at 90°, gently press forearm down. More scapular stabilization than traditional sleeper stretch\n"
            "✓ Side-Lying External Rotation: With towel between ribs and arm (increases effectiveness 20-25% per EMG studies)\n"
            "✓ Light Dynamic Movement: Immediately after throwing - arm circles, band work to promote blood flow\n"
            "✓ Recovery Time: Minor soreness 2-3 days, significant inflammation 4-6 weeks with proper rest"
        )
    
    # SCAPULAR STABILIZERS
    if data.shoulder_soreness >= 3 or data.shoulder_clicking >= 3:
        muscle_education.append(
            "💪 SCAPULAR (Shoulder Blade) MUSCLES - The Hidden Problem\n\n"
            "Your Scapular Stabilizers (Often Weak in Pitchers):\n"
            "• Serratus Anterior: Pulls shoulder blade around your ribcage\n"
            "• Lower & Middle Trapezius: Control upward rotation when you raise your arm\n"
            "• Rhomboids: Keep shoulder blade positioned properly\n\n"
            
            "Why They Matter:\n"
            "Research shows pitchers have LESS scapular upward rotation than position players. This compromises your "
            "shoulder joint and increases injury risk. These muscles position your shoulder blade so your arm can move safely. "
            "When they're weak, you get clicking, instability, and compensatory rotator cuff stress.\n\n"
            
            "RECOVERY & STRENGTHENING:\n"
            "✓ Prone Y's, T's, W's: Lie face down, move arms through these letters. Targets lower/middle traps. 3 sets x 15 reps\n"
            "✓ Scapular Wall Slides: Forearms against wall, slide up while keeping shoulder blades down and together\n"
            "✓ Serratus Push-Ups: At top of push-up, push shoulder blades apart (protraction) to activate serratus\n"
            "✓ Band Pull-Aparts: Focus on squeezing shoulder blades together\n"
            "✓ Foam Roll Thoracic Spine: Rounded upper back prevents good scapular movement"
        )
    
    # FOREARM/ELBOW SORENESS
    if data.forearm_tightness >= 3 or data.inner_elbow_pain >= 2:
        muscle_education.append(
            "💪 FOREARM FLEXOR-PRONATOR SORENESS - Tommy John Prevention Zone\n\n"
            "Your Forearm Muscles (Working Overtime):\n"
            "• Flexor Carpi Radialis & Ulnaris: Flex your wrist\n"
            "• Pronator Teres: Turns your palm down\n"
            "These attach on the inner elbow where you're feeling tightness/pain\n\n"
            
            "Why They're Sore:\n"
            "These muscles provide DYNAMIC SUPPORT to protect your UCL (ulnar collateral ligament - the Tommy John ligament). "
            "They experience extreme eccentric contractions as your wrist rapidly decelerates during ball release. "
            "When they're fatigued or strained, your UCL takes MORE stress, increasing Tommy John risk.\n\n"
            
            "CRITICAL RECOVERY:\n"
            "⚠️ Even MILD forearm strains need 7-10 days complete rest from throwing\n"
            "✓ Gradual Return-to-Throw: Another 7-10 days progressive throwing before full intensity\n"
            "✓ Total Recovery Time: 2-6+ weeks depending on severity\n"
            "✓ Wrist Flexion Stretches: Extend arm, pull fingers back gently with other hand\n"
            "✓ Heat Therapy: Increases blood flow to tendons (NOT ice)\n"
            "✓ Massage/Foam Rolling: Forearm muscles from elbow to wrist\n"
            "✓ DO NOT pitch through this pain - that's how UCL tears happen"
        )
    
    # LOWER BODY SORENESS
    if data.quad_soreness >= 3 or data.glute_activation >= 3 or data.hip_flexor_tightness >= 3:
        lower_body_muscles = []
        
        if data.quad_soreness >= 3:
            lower_body_muscles.append(
                "QUADRICEPS (Front of Thigh) - Your Deceleration Absorbers:\n"
                "Your lead leg quads experience MASSIVE eccentric loading as they decelerate your entire body at foot strike. "
                "This is like doing a single-leg squat while catching a falling weight - intense muscle damage causes DOMS.\n\n"
                "Recovery:\n"
                "✓ Light Static Stretching: Hold 30+ seconds when muscles are warm\n"
                "✓ Foam Rolling: Slow rolls on quads, IT band\n"
                "✓ Active Recovery: Light cycling or walking day after pitching\n"
                "✓ Dynamic Stretching: Leg swings, walking lunges before throwing\n"
                "✓ Recovery Time: 24-48 hours for normal DOMS"
            )
        
        if data.glute_activation >= 3:
            lower_body_muscles.append(
                "GLUTES (Butt Muscles) - Your Power Generators:\n"
                "Gluteus maximus and medius are what POWER your throw and directly increase velocity through the kinetic chain. "
                "They generate ground force that transfers up through your body to your arm.\n\n"
                "Recovery & Activation:\n"
                "✓ Glute Bridges: Before throwing to 'wake up' glutes\n"
                "✓ Hip Flow Circuits: Restore mobility lost from repetitive pitching motion\n"
                "✓ Pigeon Pose: Yoga stretch for glutes and hip rotators\n"
                "✓ Foam Rolling: Glutes and piriformis\n"
                "✓ High-Intensity Lower Body Training: DAY AFTER pitching (promotes blood flow)"
            )
        
        if data.hip_flexor_tightness >= 3:
            lower_body_muscles.append(
                "HIP FLEXORS (Front of Hip) - Your Leg Lifters:\n"
                "Iliopsoas and rectus femoris lift your stride leg during wind-up. Repetitive motion causes tightness and DOMS.\n\n"
                "Recovery:\n"
                "✓ Kneeling Hip Flexor Stretch: Back knee on ground, push hips forward\n"
                "✓ Standing Quad Stretch: Also stretches rectus femoris (crosses both hip and knee)\n"
                "✓ Avoid Prolonged Sitting: Shortens hip flexors further\n"
                "✓ Dynamic Warm-Up: Leg swings, walking lunges before pitching"
            )
        
        if lower_body_muscles:
            muscle_education.append(
                "💪 LOWER BODY SORENESS - The Foundation of Pitching Power\n\n"
                "Why Lower Body Soreness Matters:\n"
                "Your legs and hips POWER the throw. Weak or sore lower body forces you to compensate by 'arming' pitches, "
                "which dramatically increases shoulder/elbow injury risk. Research shows lower body strength directly correlates with velocity.\n\n"
                + "\n\n".join(lower_body_muscles)
            )
    
    # TRICEPS/BICEPS SORENESS
    if data.triceps_fatigue >= 3 or data.biceps_pain >= 3:
        muscle_education.append(
            "💪 ARM MUSCLE SORENESS (Triceps/Biceps)\n\n"
            "TRICEPS - Your Elbow Extender:\n"
            "Works eccentrically to control elbow flexion during late cocking, then concentrically to extend elbow during acceleration. "
            "Fatigue here can indicate you're overthrowing or have poor mechanics.\n\n"
            
            "BICEPS - Warning Sign for Labrum Issues:\n"
            "The long head of your biceps attaches to the top of your shoulder socket at the labrum (SLAP tear location). "
            "Biceps pain, especially deep in the shoulder, can indicate labral stress.\n\n"
            
            "Recovery:\n"
            "✓ Light Eccentric Training: Slowly lower weights to strengthen muscle lengthening\n"
            "✓ Heat Before Throwing: Prepare muscles for work\n"
            "✓ Avoid Heavy Bicep Curls: During season - can fatigue biceps and affect throwing\n"
            "✓ If Biceps Pain Persists: Get evaluated for labrum issues"
        )
    
    # ===== UNIVERSAL RECOVERY SCIENCE =====
    muscle_education.append(
        "🔬 THE SCIENCE OF MUSCLE RECOVERY (Evidence-Based)\n\n"
        "Why Soreness Happens (DOMS - Delayed Onset Muscle Soreness):\n"
        "• Eccentric contractions (muscle lengthening under load) cause micro-tears in muscle fibers\n"
        "• Inflammation increases growth factors that trigger satellite cells\n"
        "• This process makes you STRONGER - it's not something to fight with ice or NSAIDs\n\n"
        
        "The 4 Keys to Recovery:\n"
        "1. BLOOD FLOW: Brings nutrients in, removes waste out (why active recovery beats ice)\n"
        "2. PROTEIN SYNTHESIS: Need 20-30g protein post-pitching for muscle repair\n"
        "3. MYOKINES: Hormones released during muscle activation that drive tissue regeneration\n"
        "4. TISSUE REMODELING: Requires mechanical stress (light movement, not bed rest)\n\n"
        
        "ONLY active recovery accomplishes all 4 goals. Ice shuts down blood flow and delays healing.\n\n"
        
        "Recovery Timeline:\n"
        "• 24 Hours: Medial elbow tissue recovers to baseline - can resume light throwing\n"
        "• 48 Hours: Most DOMS peaks then begins improving\n"
        "• 3-4 Days: Needed between high-intensity outings for full recovery\n"
        "• 4-6 Weeks: Significant tendon inflammation requires this much rest\n\n"
        
        "Critical Recovery Pillars:\n"
        "💧 HYDRATION: Divide bodyweight in half = ounces needed daily (180 lbs = 90 oz water)\n"
        "🍗 NUTRITION: Protein + carbs within 2 hours post-pitching\n"
        "😴 SLEEP: 7-9 hours - when muscles actually repair and rebuild\n"
        "🔄 ACTIVE RECOVERY: Light movement next day (NOT rest)\n"
        "🚫 AVOID: Ice (delays healing), NSAIDs/Ibuprofen (blocks beneficial inflammation), Long-distance running (zaps power)"
    )
    
    # Only include muscle education if there's actual soreness
    if muscle_education:
        lines.append("=" * 60)
        lines.append("MUSCLE SORENESS EDUCATION - What's Sore & How to Recover")
        lines.append("=" * 60)
        lines.extend(muscle_education)
    # ===== ARM HEALTH EDUCATION =====
    arm_health = []
    
    if scores["arm_load"] > 6:
        arm_health.append(
            "Arm Load Assessment\n"
            "Your arm is showing significant fatigue. Key facts:\n"
            "• Rotator cuff injuries are the #1 cause of season-ending injuries in pitchers\n"
            "• 57% of pitchers experience some shoulder injury during a season\n"
            "• Focus on scapular stabilization exercises and posterior capsule stretching\n"
            "• Strengthen core, hips, and legs - weakness here forces you to 'arm' pitches which increases injury risk"
        )
    elif scores["arm_load"] > 4:
        arm_health.append(
            "Arm Load Assessment\n"
            "Moderate arm fatigue detected. Preventive care:\n"
            "• Continue rotator cuff strengthening (band work below shoulder level)\n"
            "• Stretch: focus on shoulder internal rotators and posterior capsule\n"
            "• Monitor for warning signs: decreased velocity, command loss, pain during acceleration"
        )
    else:
        arm_health.append(
            "Arm Load Assessment\n"
            "Arm metrics are healthy. Maintain your conditioning:\n"
            "• Keep up with daily band work and stretching\n"
            "• Monitor pitch counts: stay under age-appropriate limits\n"
            "• Remember: fatigue is when injuries happen - never throw through pain"
        )
    
    lines.extend(arm_health)
    
    # ===== WORKLOAD MANAGEMENT =====
    workload_advice = []
    
    # Age-appropriate pitch count guidance
    pitch_limits = {
        "9-10": 75,
        "11-12": 85,
        "13-16": 95,
        "17-18": 105
    }
    
    if data.pitches_today > 85:  # Assuming typical youth/HS age
        workload_advice.append(
            f"Pitch Count Warning\n"
            "You threw {data.pitches_today} pitches today. Safe limits:\n"
            "• Ages 9-10: 75 max\n"
            "• Ages 11-12: 85 max\n"
            "• Ages 13-16: 95 max\n"
            "• Ages 17-18: 105 max\n"
            "Research proves: Exceeding these limits dramatically increases Tommy John risk."
        )
    
    if data.rest_days < 2 and data.pitches_7d > 200:
        workload_advice.append(
            f"Rest Protocol\n"
            "You've thrown {data.pitches_7d} pitches with only {data.rest_days} rest days this week. "
            "Minimum guidelines:\n"
            "• After 25+ pitches: 1 day rest required\n"
            "• After 50+ pitches: 2 days rest required\n"
            "• After 75+ pitches: 3 days rest required\n"
            "• NO competitive pitching more than 8 months per year"
        )
    
    lines.extend(workload_advice)
    
    # ===== MECHANICS & PERFORMANCE =====
    mechanics_check = []
    
    if data.velocity_drop >= 4 or data.arm_slot_change >= 4 or data.command_loss >= 4:
        mechanics_check.append(
            "Mechanics Warning\n"
            "Performance metrics show potential mechanical breakdown:\n"
            "• Velocity drop, arm slot changes, and command loss are WARNING SIGNS of fatigue and impending injury\n"
            "• When mechanics break down, injury risk increases dramatically\n"
            "• STOP THROWING when you notice these signs - your body is telling you it's overworked\n"
            "• Work with a pitching coach to ensure you're using proper mechanics that engage your legs, core, and hips"
        )
    
    lines.extend(mechanics_check)
    
    # ===== LOWER BODY ASSESSMENT =====
    lower_body_advice = []
    
    if scores["lower_body"] > 6:
        lower_body_advice.append(
            "Lower Body Assessment\n"
            "Significant leg fatigue detected. This WILL lead to arm injuries if not addressed:\n"
            "• Weak legs/hips force you to compensate by throwing harder with your arm = injury\n"
            "• Focus on glute activation, hip mobility, and core strength\n"
            "• Dynamic stretching before throwing (leg swings, walking lunges)\n"
            "• Remember: velocity comes from legs and trunk, NOT your arm"
        )
    elif scores["lower_body"] > 4:
        lower_body_advice.append(
            "Lower Body Assessment\n"
            "Some leg tightness noted. Prevention tips:\n"
            "• Add dynamic lower body stretches to pre-throw warmup\n"
            "• Strengthen glutes and hip flexors to maintain drive off the mound\n"
            "• Tight quads, hamstrings can lead to compensatory arm stress"
        )
    
    lines.extend(lower_body_advice)
    
    # ===== MENTAL/RECOVERY STATE =====
    if scores["mental"] > 6 or scores["recovery"] > 6:
        lines.append(
            "Recovery & Mental State\n"
            "Your recovery metrics show you may be under-recovering:\n"
            "• Sleep 7-9 hours per night - this is when muscles repair\n"
            "• Stay hydrated throughout the day (not just during games)\n"
            "• High stress and poor recovery dramatically increase injury risk\n"
            "• Consider taking an extra rest day to fully recover"
        )
    
    # ===== OVERALL SUMMARY =====
    lines.append(
        f"\nOverall Risk Assessment\n"
        f"Total Risk Score: {scores['total_risk']}/10\n"
        f"• Arm Load: {scores['arm_load']}/10\n"
        f"• Workload: {scores['workload']}/10\n"
        f"• Recovery: {scores['recovery']}/10\n"
        f"• Mental: {scores['mental']}/10\n"
        f"• Lower Body: {scores['lower_body']}/10\n\n"
        f"Remember: Pain is NOT normal. If you experience sharp pain, stop throwing immediately and seek medical evaluation."
    )
    
    return "\n\n".join(lines)

# ======== API Route ========
@router.post("/risk")
async def compute_pitcher_risk(intake: PitcherIntake):
    scores = weighted_score(intake)
    feedback = generate_feedback(scores, intake)
    return {
        "status": "ok",
        "risk_score": scores["total_risk"],
        "feedback": feedback
    }