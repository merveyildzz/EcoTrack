"""
WebSocket Consumers for Real-time Social Features
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.auth import login
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """Real-time notifications for users"""
    
    async def connect(self):
        """Connect to personal notification channel"""
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Create a personal notification channel for the user
        self.notification_group = f"user_{self.user.id}_notifications"
        
        # Join notification group
        await self.channel_layer.group_add(
            self.notification_group,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.user.email} connected to notifications")
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'status': 'connected',
            'message': 'Connected to real-time notifications'
        }))
    
    async def disconnect(self, close_code):
        """Disconnect from notification channel"""
        if hasattr(self, 'notification_group'):
            await self.channel_layer.group_discard(
                self.notification_group,
                self.channel_name
            )
        logger.info(f"User disconnected from notifications: {close_code}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'unknown')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
    
    async def notification_message(self, event):
        """Send notification to user"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification_type': event['notification_type'],
            'title': event['title'],
            'message': event['message'],
            'data': event.get('data', {}),
            'timestamp': event['timestamp']
        }))


class LeaderboardConsumer(AsyncWebsocketConsumer):
    """Real-time leaderboard updates"""
    
    async def connect(self):
        """Connect to leaderboard updates"""
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Get leaderboard type from URL params
        self.leaderboard_type = self.scope['url_route']['kwargs'].get('type', 'global')
        self.leaderboard_group = f"leaderboard_{self.leaderboard_type}"
        
        # Join leaderboard group
        await self.channel_layer.group_add(
            self.leaderboard_group,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.user.email} connected to leaderboard: {self.leaderboard_type}")
        
        # Send current leaderboard data
        await self.send_leaderboard_data()
    
    async def disconnect(self, close_code):
        """Disconnect from leaderboard channel"""
        if hasattr(self, 'leaderboard_group'):
            await self.channel_layer.group_discard(
                self.leaderboard_group,
                self.channel_name
            )
        logger.info(f"User disconnected from leaderboard: {close_code}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'unknown')
            
            if message_type == 'refresh':
                await self.send_leaderboard_data()
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
    
    @sync_to_async
    def get_leaderboard_data(self):
        """Fetch current leaderboard data"""
        from .models import Leaderboard, LeaderboardEntry
        
        try:
            # Get the leaderboard configuration
            leaderboard = Leaderboard.objects.filter(
                leaderboard_type=self.leaderboard_type,
                is_active=True
            ).first()
            
            if not leaderboard:
                return []
            
            # Get top entries
            entries = LeaderboardEntry.objects.filter(
                leaderboard=leaderboard
            ).select_related('user')[:20]
            
            return [
                {
                    'rank': entry.rank,
                    'user_id': str(entry.user.id),
                    'username': entry.user.username,
                    'score': entry.score,
                    'rank_change': entry.rank_change
                }
                for entry in entries
            ]
        except Exception as e:
            logger.error(f"Error fetching leaderboard data: {e}")
            return []
    
    async def send_leaderboard_data(self):
        """Send current leaderboard data to client"""
        leaderboard_data = await self.get_leaderboard_data()
        
        await self.send(text_data=json.dumps({
            'type': 'leaderboard_data',
            'leaderboard_type': self.leaderboard_type,
            'entries': leaderboard_data,
            'timestamp': str(timezone.now())
        }))
    
    async def leaderboard_update(self, event):
        """Send leaderboard update to users"""
        await self.send(text_data=json.dumps({
            'type': 'leaderboard_update',
            'update_type': event['update_type'],
            'leaderboard_type': event['leaderboard_type'],
            'data': event['data'],
            'timestamp': event['timestamp']
        }))


class ChallengeConsumer(AsyncWebsocketConsumer):
    """Real-time challenge updates"""
    
    async def connect(self):
        """Connect to challenge updates"""
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Get challenge ID from URL params
        self.challenge_id = self.scope['url_route']['kwargs'].get('challenge_id')
        self.challenge_group = f"challenge_{self.challenge_id}"
        
        # Join challenge group
        await self.channel_layer.group_add(
            self.challenge_group,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.user.email} connected to challenge: {self.challenge_id}")
        
        # Send current challenge data
        await self.send_challenge_data()
    
    async def disconnect(self, close_code):
        """Disconnect from challenge channel"""
        if hasattr(self, 'challenge_group'):
            await self.channel_layer.group_discard(
                self.challenge_group,
                self.channel_name
            )
        logger.info(f"User disconnected from challenge: {close_code}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'unknown')
            
            if message_type == 'refresh':
                await self.send_challenge_data()
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
    
    @sync_to_async
    def get_challenge_data(self):
        """Fetch current challenge data"""
        from .models import Challenge, ChallengeParticipation
        
        try:
            challenge = Challenge.objects.get(id=self.challenge_id)
            
            # Get user's participation if exists
            user_participation = None
            if not self.user.is_anonymous:
                try:
                    user_participation = ChallengeParticipation.objects.get(
                        user=self.user,
                        challenge=challenge
                    )
                except ChallengeParticipation.DoesNotExist:
                    pass
            
            # Get top participants
            top_participants = ChallengeParticipation.objects.filter(
                challenge=challenge,
                is_active=True
            ).order_by('-current_progress')[:10]
            
            return {
                'challenge': {
                    'id': str(challenge.id),
                    'title': challenge.title,
                    'description': challenge.description,
                    'goal_value': challenge.goal_value,
                    'goal_unit': challenge.goal_unit,
                    'participant_count': challenge.participant_count,
                    'is_current': challenge.is_current,
                    'end_date': challenge.end_date.isoformat()
                },
                'user_participation': {
                    'is_participating': user_participation is not None,
                    'current_progress': user_participation.current_progress if user_participation else 0,
                    'progress_percentage': user_participation.progress_percentage if user_participation else 0,
                    'is_completed': user_participation.is_completed if user_participation else False
                } if user_participation else None,
                'top_participants': [
                    {
                        'username': p.user.username,
                        'progress': p.current_progress,
                        'progress_percentage': p.progress_percentage,
                        'is_completed': p.is_completed
                    }
                    for p in top_participants
                ]
            }
        except Challenge.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error fetching challenge data: {e}")
            return None
    
    async def send_challenge_data(self):
        """Send current challenge data to client"""
        challenge_data = await self.get_challenge_data()
        
        if challenge_data:
            await self.send(text_data=json.dumps({
                'type': 'challenge_data',
                'data': challenge_data,
                'timestamp': str(timezone.now())
            }))
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Challenge not found'
            }))
    
    async def challenge_update(self, event):
        """Send challenge update to participants"""
        await self.send(text_data=json.dumps({
            'type': 'challenge_update',
            'update_type': event['update_type'],
            'data': event['data'],
            'timestamp': event['timestamp']
        }))