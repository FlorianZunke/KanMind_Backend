from rest_framework import serializers
from django.core.validators import EmailValidator
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, PermissionDenied


from kanban_app.models import Board, Comment, User, Task


class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(read_only=True)
    tasks_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)
    owner_id = serializers.IntegerField(read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True
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
        """
        Create and return a new Board instance, given the validated data.

        This method handles the creation of the Board object and sets the members 
        based on the provided input. Additionally, it ensures that the current 
        authenticated user (from the request context) is added as a member of the board.

        Args:
            validated_data (dict): The validated data from the serializer input.

        Returns:
            Board: The newly created Board instance with members set.
        """
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
        return obj.username


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
            'comments_count',
        ]

    
    def get_comments_count(self, obj):
        """
        Return the count of comments related to the given object.

        Args:
            obj (Model instance): The instance (e.g., a Task) for which comments are counted.

        Returns:
            int: Number of comments if the 'comments' related manager exists, otherwise 0.
        """
        return obj.comments.count() if hasattr(obj, 'comments') else 0
    

    
    def validate(self, data):
        """
        Validate the incoming data to ensure the user has permission to access the related board.

        Checks that:
        - The board field is present in the data.
        - The requesting user is either the owner or a member of the board.

        Args:
            data (dict): The deserialized input data.

        Raises:
            NotFound: If the board is not provided.
            PermissionDenied: If the user is not a member or owner of the board.

        Returns:
            dict: The validated data unchanged if all checks pass.
        """
        request = self.context['request']
        user = request.user
        board = data.get('board')

        if not board:
            raise NotFound(detail="Board ist erforderlich.")

        if not (user == board.owner or user in board.members.all()):
            raise PermissionDenied(detail= "Zugriff verweigert. Du bist kein Mitglied dieses Boards.")

        return data

    
    def create(self, validated_data):
        """
        Create and return a new Task instance, setting the author to the current user.

        Args:
            validated_data (dict): The validated data from the serializer input.

        Returns:
            Task: The newly created Task instance.
        """
        request = self.context['request']
        validated_data['author'] = request.user
        return super().create(validated_data)


class BoardDetailReadSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(read_only=True)
    members = MiniUserSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner_id',
            'members',
            'tasks',
        ]

    
class BoardDetailWriteSerializer(serializers.ModelSerializer):
    owner_data = MiniUserSerializer(source='owner',read_only=True)
    members_data = MiniUserSerializer(source='members',many=True, read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner_data',
            'members_data',
            'members',
        ]

    def update(self, instance, validated_data):
        """
        Update an existing Board instance with the provided validated data.

        - Updates the board's title if a new title is provided.
        - Optionally updates the board's member list based on the provided PK list.
        - Ensures that the board owner is always included in the members.

        Args:
            instance (Board): The Board instance to be updated.
            validated_data (dict): The validated input data, potentially including:
                - 'title' (str): The new title for the board.
                - 'members' (list of User): The list of User instances to set as members.

        Returns:
            Board: The updated Board instance with its title and members updated.
        """
        members = validated_data.pop('members', None)
        instance.title = validated_data.get('title', instance.title)
        instance.save()

        if members is not None:
            if instance.owner not in members:
                members.append(instance.owner)
            instance.members.set(members)

        return instance

class TaskDetailSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'status',
            'priority',
            'assignee_id',
            'assignee',
            'reviewer_id',
            'reviewer',
            'due_date',
        ]

class EmailCheckSerializer(serializers.Serializer):

    email = serializers.EmailField(
        validators=[EmailValidator()],
        required=True,
        error_messages={
            "invalid": "Ungültiges Format. Bitte eine gültige E-Mail-Adresse angeben."
        }
    )

    
    def validate_email(self, value):
        """
        Validate that the given email exists in the User model.

        Args:
            value (str): The email address to validate.

        Raises:
            serializers.ValidationError: If no user with the given email exists.

        Returns:
            str: The validated email address.
        """
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("E-Mail nicht gefunden.")
        
        self.user = user
        return value
    
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']

    
    def validate(self, data):
        """
        Validate that the current user is a member or owner of the task's board.

        Raises a ValidationError if the user is not part of the board.

        Also retrieves the Task instance based on the task_id from the context
        and stores it on the serializer instance for later use in creation.

        Args:
            data (dict): The data to validate.

        Returns:
            dict: The validated data.
        """
        request = self.context['request']
        task_id = self.context.get('task_id')
        user = request.user

        task = get_object_or_404(Task, id=task_id)
        
        if user != task.board.owner and user not in task.board.members.all():
            raise serializers.ValidationError("Du bist kein Mitglied dieses Boards.")

        self.task = task

        return data
    
    def create(self, validated_data):
        """
        Create a new instance with the current user as author and the validated task.

        Args:
            validated_data (dict): The validated data for creating the object.

        Returns:
            Model instance: The newly created model instance.
        """
        validated_data['author'] = self.context['request'].user
        validated_data['task'] = self.task
        return super().create(validated_data)
            
