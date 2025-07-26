from rest_framework import serializers
from kanban_app.models import Board
from ..models import User, Task
from django.core.validators import EmailValidator

class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(read_only=True)
    tasks_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)
    owner_id = serializers.IntegerField(read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )
    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'members',
            'member_count',
            'tasks_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id'
        ]

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        board.members.set(members)
        board.members.add(self.context['request'].user)
        return board
     
class MiniUserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'fullname'
        ]

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class TaskSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assigned_to',
        queryset=User.objects.all(), 
        write_only=True, 
        required=False
    )

    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer',
        queryset=User.objects.all(), 
        write_only=True,
        required=False
    )

    assignee = MiniUserSerializer(source='assigned_to', read_only=True)
    reviewer = MiniUserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    class Meta:
        model = Task
        fields = [
            'id',
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee_id',
            'assignee',
            'reviewer_id',
            'reviewer',
            'due_date',
            'comments_count'
        ]

    def get_comments_count(self, obj):
        return obj.comments.count() if hasattr(obj, 'comments') else 0
    

class BoardDetailSerializer(serializers.ModelSerializer):
    members = MiniUserSerializer(many=True, read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True, required=False
    )
    tasks = TaskSerializer(many=True, read_only=True)
    member_count = serializers.ReadOnlyField()
    tasks_count = serializers.ReadOnlyField()
    tasks_to_do_count = serializers.ReadOnlyField()
    tasks_high_prio_count = serializers.ReadOnlyField()
    class Meta:
        model = Board
        fields = [
            'id', 
            'title', 
            'owner_id', 
            'members',
            'member_ids', 
            'member_count', 
            'tasks_count',
            'tasks_to_do_count', 
            'tasks_high_prio_count',
            'tasks'
        ]

    def update(self, instance, validated_data):
        member_ids = validated_data.pop('member_ids', None)

        instance.title = validated_data.get('title', instance.title)
        instance.save()

        if member_ids is not None:
            if instance.owner.id not in member_ids:
                member_ids.append(instance.owner.id)

            instance.members.set(member_ids)

        return instance
    

class TaskDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = [
            'id', 
            'title', 
            'description', 
            'status',
            'priority', 
            'due_date'
        ]

class EmailCheckSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[EmailValidator()],
        required=True,
        error_messages={
            "required": "Bitte gib eine E-Mail-Adresse an.",
            "invalid": "Ungültiges Format. Bitte eine gültige E-Mail-Adresse angeben."
        }
    )
