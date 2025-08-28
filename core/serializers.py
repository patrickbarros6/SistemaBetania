from rest_framework import serializers
from .models import Member, MemberPref, Unavailability, SurveyCampaign, SurveyInvite
class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"
class MemberPrefSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.name", read_only=True)
    class Meta:
        model = MemberPref
        fields = ("member","member_name","language")
class UnavailabilitySerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.name", read_only=True)
    class Meta:
        model = Unavailability
        fields = "__all__"
class CampaignSerializer(serializers.ModelSerializer):
    total_invites = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = SurveyCampaign
        fields = ("id","year","month","created_at","message_template","total_invites")
    def get_total_invites(self, obj):
        return SurveyInvite.objects.filter(campaign=obj).count()
class InviteSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.name", read_only=True)
    class Meta:
        model = SurveyInvite
        fields = ("id","campaign","member","member_name","token","sent_at","responded_at","reminders_sent","last_reminder_at","available_all")
