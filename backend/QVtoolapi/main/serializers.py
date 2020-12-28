from rest_framework import serializers
from django.contrib.auth import authenticate
from guardian.shortcuts import assign_perm
from django.utils.translation import gettext_lazy as _

from .models import Process, Election, Vote, Proposal, Delegate, Conversation
from django.contrib.auth.models import (User, Group, Permission)


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = '__all__'


class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = '__all__'


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'

    def create(self, validated_data):
        election = Election.objects.get(pk=self.context.get("election_id"))
        sender = validated_data['sender']
        assign_perm('can_view_results', sender, election)

        vote = Vote.objects.create(
            sender=sender,
            proposal=validated_data['proposal'],
            amount=validated_data['amount'],
            date=validated_data['date'],
        )
        return vote


class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class ProcessSerializer(serializers.ModelSerializer):
    conversation = ConversationSerializer(required=False)
    election = ElectionSerializer(required=False)

    class Meta:
        model = Process
        fields = '__all__'

    def create(self, validated_data):
        conversation_data = validated_data.get('conversation')
        if conversation_data is not None:
            conversation = ConversationSerializer.create(
                ConversationSerializer(),
                validated_data=conversation_data,
                )
        election_data = validated_data.get('election')
        if election_data is not None:
            election = ElectionSerializer.create(
                ElectionSerializer(),
                validated_data=election_data,
            )
        process, created = Process.objects.update_or_create(
            title=validated_data.get('title'),
            description=validated_data.get('description'),
            start_date=validated_data.get('start_date'),
            end_date=validated_data.get('end_date'),
            matching_pool=validated_data.get('matching_pool'),
            conversation=conversation,
            curation_info=validated_data.get('curation_info'),
            top_posts=validated_data.get('top_posts', []),
            election=election,
            )
        process.groups.set(validated_data.get('groups', []))
        process.delegates.set(validated_data.get('delegates', []))
        return process


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': False},
            'email': {'required': True},
            }

    def create(self, validated_data, is_autogenerated):
        """
        autogenerated user: set uuid as username.

        standard user: conceal password and set email as username.
        """
        if is_autogenerated:
            validated_data['username'] = validated_data.get('password', '')
        else:
            validated_data['username'] = validated_data.get('email', '')
        user = User(
            username=validated_data.get('username'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email'),
            is_staff=validated_data.get('is_staff', False),
            is_superuser=validated_data.get('is_superuser', False),
        )
        user.set_password(validated_data['password'])
        user.save()
        user.groups.set(validated_data.get('groups', []))
        return user


class DelegateSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Delegate
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.get('user')
        is_autogenerated = validated_data.get('is_autogenerated', False)
        user = UserSerializer.create(
            UserSerializer(),
            validated_data=user_data,
            is_autogenerated=is_autogenerated)
        delegate, created = Delegate.objects.update_or_create(
            user=user,
            is_autogenerated=is_autogenerated,
            profile_pic=validated_data.get('profile_pic'),
            phone_number=validated_data.get('phone_number', ''),
            invited_by=validated_data.get('invited_by'),
            credit_balance=validated_data.get('credit_balance', 0),
            )
        return delegate


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(
        label=_("Email"),
        write_only=True
        )
    password = serializers.CharField(
        label=_("Password",),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            """
            The authenticate call simply returns None for is_active=False
            users. (Assuming the default ModelBackend authentication
            backend.)
            """
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
