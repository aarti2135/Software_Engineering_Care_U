from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count
from .models import NutritionEntry, HealthReminder


class HealthCalculator:
    """
    Calculates personalized health metrics based on user profile.
    Uses Mifflin-St Jeor equation for BMR and Harris-Benedict for TDEE.
    """

    ACTIVITY_MULTIPLIERS = {
        'sedentary': 1.2,  # Little or no exercise
        'light': 1.375,  # Light exercise 1-3 days/week
        'moderate': 1.55,  # Moderate exercise 3-5 days/week
        'active': 1.725,  # Hard exercise 6-7 days/week
        'very_active': 1.9  # Very hard exercise & physical job
    }

    @staticmethod
    def calculate_bmr(profile):
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor equation.
        Returns None if insufficient data.
        """
        if not all([profile.weight_kg, profile.height_cm, profile.age, profile.sex]):
            return None

        weight = float(profile.weight_kg)
        height = float(profile.height_cm)
        age = profile.age

        # Mifflin-St Jeor equation
        if profile.sex == 'male':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:  # female or other (use female formula as default)
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

        return bmr

    @staticmethod
    def calculate_tdee(profile, activity_level='sedentary'):
        """
        Calculate Total Daily Energy Expenditure.
        Returns None if BMR cannot be calculated.
        """
        bmr = HealthCalculator.calculate_bmr(profile)
        if not bmr:
            return None

        activity_level = HealthCalculator.get_activity_level(profile)
        multiplier = HealthCalculator.ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
        return bmr * multiplier

    @staticmethod
    def calculate_protein_target(profile, activity_level='sedentary'):
        """
        Calculate daily protein target in grams.
        Ranges from 0.8g/kg (sedentary) to 2.0g/kg (very active).
        """
        if not profile.weight_kg:
            return None

        weight = float(profile.weight_kg)

        # Protein multipliers based on activity
        protein_multipliers = {
            'sedentary': 0.8,
            'light': 1.0,
            'moderate': 1.2,
            'active': 1.6,
            'very_active': 2.0
        }

        activity_level = HealthCalculator.get_activity_level(profile)
        multiplier = protein_multipliers.get(activity_level, 0.8)
        return weight * multiplier

    @staticmethod
    def get_activity_level(profile):
        """
        Determine activity level.
        TODO: Can be enhanced to infer from step count data.
        For now, defaults to sedentary if not specified.
        """
        # Check if profile has activity_level field (you might add this later)
        if hasattr(profile, 'activity_level') and profile.activity_level:
            return profile.activity_level

        # Default to sedentary
        return 'sedentary'


class GoalsIntegration:
    """
    Hook point for future goals integration.
    When Goals model is built, implement these methods.
    """

    @staticmethod
    def has_nutrition_goals(user):
        """Check if user has set nutrition-related goals."""
        # TODO: Implement when Goals model exists
        # Example: return user.fitness_goals.filter(goal_type='nutrition').exists()
        return False

    @staticmethod
    def get_calorie_target_from_goals(user):
        """Get calorie target from user's goals."""
        # TODO: Implement when Goals model exists
        # Example: return user.fitness_goals.get(goal_type='weight').target_calories
        return None

    @staticmethod
    def get_protein_target_from_goals(user):
        """Get protein target from user's goals."""
        # TODO: Implement when Goals model exists
        return None


class ExplanationGenerator:
    """
    Generates explanations for health reminders.
    Sprint 2: Pre-written templates with personalized data
    Sprint 3+: AI-generated via LangGraph (replace methods here)
    """

    @staticmethod
    def get_low_calorie_explanation(avg_calories, target_calories, profile):
        """Generate explanation for low calorie intake."""
        activity = HealthCalculator.get_activity_level(profile)

        return f"""
Your recent average of {avg_calories:.0f} calories per day is significantly below 
your recommended target of {target_calories:.0f} calories per day (calculated based 
on your profile: {profile.age}yo, {profile.weight_kg}kg, {profile.height_cm}cm, 
{activity} activity level).

Consistently low calorie intake can lead to:

• Decreased energy levels and chronic fatigue
• Loss of muscle mass (your body breaks down muscle for fuel)
• Weakened immune system and slower recovery
• Slower metabolism (your body adapts to low energy)
• Nutrient deficiencies affecting overall health
• Difficulty concentrating and mood changes

Your body needs adequate fuel to function optimally, support your daily activities, 
maintain muscle mass, and protect your long-term health.
        """.strip()

    @staticmethod
    def get_inconsistent_logging_explanation(days_logged, total_days):
        """Generate explanation for inconsistent meal logging."""
        return f"""
You've logged meals on only {days_logged} out of the last {total_days} days. 
Consistent tracking is crucial for understanding your nutrition patterns because:

• It reveals hidden habits and trends you might not notice day-to-day
• It helps identify what's working and what needs adjustment
• It provides accurate data for personalized recommendations
• It keeps you accountable to your health goals
• It helps detect concerning patterns early

Think of logging as taking your health's "vital signs" - sporadic measurements 
make it difficult to get an accurate picture of your overall wellness. Even if 
you're not perfect every day, consistent tracking gives us the data needed to 
provide truly personalized guidance.
        """.strip()

    @staticmethod
    def get_low_protein_explanation(avg_protein, target_protein, profile):
        """Generate explanation for low protein intake."""
        activity = HealthCalculator.get_activity_level(profile)

        return f"""
Your average protein intake of {avg_protein:.1f}g per day is below your recommended 
target of {target_protein:.0f}g per day (calculated as {target_protein / float(profile.weight_kg):.1f}g 
per kg body weight for your {activity} activity level).

Adequate protein is essential for:

• Building and repairing muscle tissue after activity
• Supporting immune function and fighting illness
• Maintaining healthy skin, hair, and nails
• Producing enzymes and hormones your body needs
• Keeping you feeling full and satisfied (reducing snacking)
• Preserving muscle mass during weight loss
• Recovery and adaptation from exercise

Protein needs increase with activity level. Your target is personalized based on 
your weight ({profile.weight_kg}kg) and activity patterns.
        """.strip()

    @staticmethod
    def get_incomplete_profile_explanation():
        """Explain why complete profile data is needed."""
        return """
To provide you with personalized, accurate health recommendations, we need some 
basic information about you: your age, weight, height, and sex.

This data allows us to:

• Calculate your Basal Metabolic Rate (BMR) - calories needed at rest
• Determine your Total Daily Energy Expenditure (TDEE)
• Set personalized targets for calories, protein, and macronutrients
• Detect concerning patterns specific to YOUR body
• Give advice that's actually relevant to your situation

Without this information, any recommendations would be generic and potentially 
inaccurate for your specific needs. Your data is private and only used to 
personalize YOUR experience.
        """.strip()


class ReminderEngine:
    """
    Analyzes user health data and generates personalized reminders.
    Calculates targets based on profile data, with hooks for future goals integration.
    """

    def __init__(self, user):
        self.user = user
        self.profile = user.profile
        self.calculator = HealthCalculator()
        self.goals = GoalsIntegration()
        self.explanation_gen = ExplanationGenerator()
        self.activity_level = self.calculator.get_activity_level(self.profile)

    def analyze_and_create_reminders(self):
        """
        Main entry point: analyzes all health data and creates reminders.
        Returns list of newly created reminders.
        """
        new_reminders = []

        # First check if profile is complete
        reminder = self.check_profile_completion()
        if reminder:
            new_reminders.append(reminder)
            # If profile incomplete, skip other checks (we need data first)
            return new_reminders

        # Check each health pattern
        reminder = self.check_calorie_intake()
        if reminder:
            new_reminders.append(reminder)

        reminder = self.check_logging_consistency()
        if reminder:
            new_reminders.append(reminder)

        reminder = self.check_protein_intake()
        if reminder:
            new_reminders.append(reminder)

        return new_reminders

    def check_profile_completion(self):
        """Check if user has completed essential profile information."""
        missing_fields = []

        if not self.profile.age:
            missing_fields.append('age')
        if not self.profile.weight_kg:
            missing_fields.append('weight')
        if not self.profile.height_cm:
            missing_fields.append('height')
        if not self.profile.sex:
            missing_fields.append('sex')


        if not missing_fields:
            return None

        # Check if we already reminded them recently
        existing = HealthReminder.objects.filter(
            user=self.user,
            reminder_type='general',
            title='Complete Your Profile',
            created_at__gte=timezone.now() - timedelta(days=3)
        ).exists()

        if existing:
            return None

        fields_str = ', '.join(missing_fields)

        reminder = HealthReminder.objects.create(
            user=self.user,
            reminder_type='general',
            title='Complete Your Profile',
            message=f'Please add your {fields_str} to receive personalized health recommendations.',
            explanation=self.explanation_gen.get_incomplete_profile_explanation(),
            priority='medium',
            actionable_steps=[
                'Go to your profile settings',
                f'Fill in missing information: {fields_str}',
                'Update your activity level if available',
                'Save your changes to unlock personalized insights'
            ]
        )
        return reminder

    def get_calorie_target(self):
        """
        Get personalized calorie target.
        Checks goals first (future), falls back to TDEE calculation.
        """
        # Check for goal-based target (future integration)
        if self.goals.has_nutrition_goals(self.user):
            goal_target = self.goals.get_calorie_target_from_goals(self.user)
            if goal_target:
                return goal_target

        # Fall back to TDEE-based calculation
        tdee = self.calculator.calculate_tdee(self.profile, self.activity_level)
        return tdee

    def get_protein_target(self):
        """
        Get personalized protein target.
        Checks goals first (future), falls back to profile-based calculation.
        """
        # Check for goal-based target (future integration)
        if self.goals.has_nutrition_goals(self.user):
            goal_target = self.goals.get_protein_target_from_goals(self.user)
            if goal_target:
                return goal_target

        # Fall back to activity-based calculation
        return self.calculator.calculate_protein_target(self.profile, self.activity_level)

    def check_calorie_intake(self):
        """Check for concerning calorie intake patterns."""
        week_ago = timezone.localdate() - timedelta(days=7)

        entries = NutritionEntry.objects.filter(
            user=self.user,
            logged_at__gte=week_ago
        )

        if not entries.exists():
            return None

        avg_calories = entries.aggregate(avg=Avg('calories'))['avg']
        target_calories = self.get_calorie_target()

        if not target_calories:
            return None  # Can't check without target

        # Check if significantly below target (less than 75%)
        if avg_calories < (target_calories * 0.75):
            # Avoid duplicate reminders
            existing = HealthReminder.objects.filter(
                user=self.user,
                reminder_type='nutrition',
                title='Low Calorie Intake Detected',
                created_at__gte=timezone.now() - timedelta(days=5)
            ).exists()

            if existing:
                return None

            deficit = target_calories - avg_calories

            reminder = HealthReminder.objects.create(
                user=self.user,
                reminder_type='nutrition',
                title='Low Calorie Intake Detected',
                message=f'Your 7-day average is {avg_calories:.0f} cal/day, about {deficit:.0f} calories below your target of {target_calories:.0f} cal/day.',
                explanation=self.explanation_gen.get_low_calorie_explanation(
                    avg_calories,
                    target_calories,
                    self.profile
                ),
                priority='high',
                actionable_steps=[
                    f'Target: {target_calories:.0f} calories per day',
                    f'Add ~{deficit:.0f} calories through healthy foods',
                    'Add a healthy snack between meals (nuts, yogurt, fruit)',
                    'Include more calorie-dense healthy foods (avocado, olive oil, nut butters)',
                    'Review your portion sizes - you might be underestimating',
                    'Consider consulting a nutritionist if this pattern continues'
                ]
            )
            return reminder

        return None

    def check_logging_consistency(self):
        """Check if user is logging meals consistently."""
        week_ago = timezone.localdate() - timedelta(days=7)

        days_with_entries = NutritionEntry.objects.filter(
            user=self.user,
            logged_at__gte=week_ago
        ).values('logged_at').distinct().count()

        # Threshold: logged less than 5 out of 7 days
        if days_with_entries < 5:
            # Avoid duplicate reminders
            existing = HealthReminder.objects.filter(
                user=self.user,
                reminder_type='general',
                title='Keep Up Your Logging Streak',
                created_at__gte=timezone.now() - timedelta(days=5)
            ).exists()

            if existing:
                return None

            reminder = HealthReminder.objects.create(
                user=self.user,
                reminder_type='general',
                title='Keep Up Your Logging Streak',
                message=f'You\'ve logged meals on {days_with_entries} out of the last 7 days. Consistency helps us give you better insights!',
                explanation=self.explanation_gen.get_inconsistent_logging_explanation(
                    days_with_entries,
                    7
                ),
                priority='low',
                actionable_steps=[
                    'Set a daily reminder on your phone to log meals',
                    'Log meals immediately after eating (don\'t wait until end of day)',
                    'Start small: commit to logging just breakfast every day this week',
                    'Use the app\'s quick-entry feature for common meals',
                    f'Goal: Log at least 6 out of 7 days per week'
                ]
            )
            return reminder

        return None

    def check_protein_intake(self):
        """Check for low protein intake patterns."""
        week_ago = timezone.localdate() - timedelta(days=7)

        entries = NutritionEntry.objects.filter(
            user=self.user,
            logged_at__gte=week_ago,
            protein_g__isnull=False
        )

        if not entries.exists():
            return None

        avg_protein = entries.aggregate(avg=Avg('protein_g'))['avg']
        target_protein = self.get_protein_target()

        if not target_protein:
            return None  # Can't check without target

        # Check if below 70% of target
        if avg_protein < (target_protein * 0.7):
            # Avoid duplicate reminders
            existing = HealthReminder.objects.filter(
                user=self.user,
                reminder_type='nutrition',
                title='Increase Your Protein Intake',
                created_at__gte=timezone.now() - timedelta(days=5)
            ).exists()

            if existing:
                return None

            deficit = target_protein - avg_protein

            reminder = HealthReminder.objects.create(
                user=self.user,
                reminder_type='nutrition',
                title='Increase Your Protein Intake',
                message=f'Your average protein intake is {avg_protein:.1f}g/day. Target: {target_protein:.0f}g/day based on your profile.',
                explanation=self.explanation_gen.get_low_protein_explanation(
                    avg_protein,
                    target_protein,
                    self.profile
                ),
                priority='medium',
                actionable_steps=[
                    f'Target: {target_protein:.0f}g protein per day',
                    f'Increase by ~{deficit:.0f}g daily',
                    'Add Greek yogurt to breakfast (15-20g protein)',
                    'Include lean chicken or fish at lunch (25-30g)',
                    'Snack on nuts or cheese (5-10g)',
                    'Consider a protein shake if needed (20-25g)'
                ]
            )
            return reminder

        return None