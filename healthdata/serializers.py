from rest_framework import serializers
from .models import NutritionEntry

class NutritionEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionEntry
        fields = [
            "id", "logged_at", "meal_type", "calories",
            "protein_g", "carbs_g", "fat_g", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        for f in ["protein_g", "carbs_g", "fat_g"]:
            v = attrs.get(f)
            if v is not None and v < 0:
                raise serializers.ValidationError({f: "Cannot be negative."})
        if attrs.get("calories", 0) < 0:
            raise serializers.ValidationError({"calories": "Cannot be negative."})
        return attrs
