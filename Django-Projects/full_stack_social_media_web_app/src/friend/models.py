from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.utils import timezone

from django.db.models.signals import post_save
from django.dispatch import receiver


from chat.utils import find_or_create_private_chat
from notification.models import Notification

class FriendList(models.Model):

    # one friend list per one user
    user                    = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
    friends                 = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="friends")

    # Fore reverse lookups
    notifications            = GenericRelation(Notification)
    def __str__(self):
        return self.user.username

    def add_friend(self, account):
        """
        Add a new friend
        """
        if not account in self.friends.all():
            self.friends.add(account)
            self.save()

            content_type = ContentType.objects.get_for_model(self)
            # Create notification
            # Notification(
            #     target=self.user,
            #     from_user=account,
            #     redirect_url=f"{settings.BASE_URL}/account/{account.pk}/",
            #     verb=f"You are now friends with {account.username}.",
            #     content_type=content_type,
            #     object_id=self.id,
            # ).save()

            self.notifications.create(
                target=self.user,
                from_user=account,
                redirect_url=f"{settings.BASE_URL}/account/{account.pk}/",
                verb=f"You are now friends with {account.username}.",
                content_type=content_type,
            )
            self.save()


            # Create a private chat (or activate an old one)
            chat = find_or_create_private_chat(self.user, account)
            if not chat.is_active:
                chat.is_active = True
                chat.save()
    
    def remove_friend(self, account):
        """
        Remove a friend
        """
        if account in self.friends.all():
            self.friends.remove(account)

            chat = find_or_create_private_chat(self.user, account)
            if chat.is_active:
                chat.is_active = False
                chat.save()

    def unfriend(self, removee):
        """
        Initiate the action of unfriending someone.
        """
        remove_friends_list = self # person terminating the friendship

        # Remove friend from remover friend list
        remove_friends_list.remove_friend(removee)

        # Remove friend from removee friend list
        friends_list = FriendList.objects.get(user=removee)
        friends_list.remove_friend(remove_friends_list.user)


        content_type = ContentType.objects.get_for_model(self)

        # Create notification for removee
        self.notifications.create(
            target=removee,
            from_user=self.user,
            redirect_url=f"{settings.BASE_URL}/account/{self.user.pk}/",
            verb=f"You are no longer friend with {self.user.username}.",
            content_type=content_type,
        )

        # Create notification for remover
        self.notifications.create(
            target=self.user,
            from_user=removee,
            redirect_url=f"{settings.BASE_URL}/account/{removee.pk}/",
            verb=f"You are no longer friend with {removee.username}.",
            content_type=content_type,
        )
        self.save()

    def is_mutual_friend(self, friend):
        """
        Is this a friend?
        """
        if friend in self.friends.all():
            return True
        return False

    @property
    def get_cname(self):
        """
        For determining what kind of object is associated with a Notification
        """
        return "FriendList"


class FriendRequest(models.Model):
    """
    A friend request consists of two main parts:

    1. SENDER:
        - Person sending/initiating the friend request
    2. RECEIVER:
        - Person receiving the friend request
    """

    sender                          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender")
    receiver                        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="receiver")
    is_active                       = models.BooleanField(blank=False, null=False, default=True)
    timestamp                       = models.DateTimeField(auto_now_add=True)

    notifications                   = GenericRelation(Notification)

    def __str__(self):
        return self.sender.username

    
    def accept(self):
        """
        Accept a friend request
        Update both SENDER and RECEIVER friend list
        """
        receiver_friend_list = FriendList.objects.get(user=self.receiver)
        if receiver_friend_list:

            content_type = ContentType.objects.get_for_model(self)

            # Update notification for RECEIVER
            receiver_notification = Notification.objects.get(target=self.receiver, content_type=content_type, object_id=self.id)

            receiver_notification.is_active = False
            receiver_notification.redirect_url = f"{settings.BASE_URL}/account/{self.sender.pk}/"
            receiver_notification.verb = f"You accepeted {self.sender.username}'s friend request."
            receiver_notification.timestamp = timezone.now()
            receiver_notification.save()

            receiver_friend_list.add_friend(self.sender)

            sender_friend_list = FriendList.objects.get(user=self.sender)
            if sender_friend_list:

                # Create notification for SENDER
                self.notifications.create(
                    target=self.sender,
                    from_user=self.receiver,
                    redirect_url=f"{settings.BASE_URL}/account/{self.receiver.pk}/",
                    verb=f"{self.receiver.username} accepted your friend request.",
                    content_type=content_type,                    
                )
                sender_friend_list.add_friend(self.receiver)
                self.is_active = False
                self.save()

            return receiver_notification

    def decline(self):
        """
        Decline a friend request.
        It is "declined" by setting the 'is_active' field to False
        """
        self.is_active = False
        self.save()

        content_type = ContentType.objects.get_for_model(self)

        # Update notification for RECEIVER
        receiver_notification = Notification.objects.get(target=self.receiver, content_type=content_type, object_id=self.id)

        # Update notification for RECEIVER
        receiver_notification = Notification.objects.get(target=self.receiver, content_type=content_type, object_id=self.id)

        receiver_notification.is_active = False
        receiver_notification.redirect_url = f"{settings.BASE_URL}/account/{self.sender.pk}/"
        receiver_notification.verb = f"You declined {self.sender.username}'s friend request."
        receiver_notification.timestamp = timezone.now()
        receiver_notification.save() 

        # Create notification for SENDER
        self.notifications.create(
            target=self.sender,
            from_user=self.receiver,
            redirect_url=f"{settings.BASE_URL}/account/{self.receiver.pk}/",
            verb=f"{self.receiver.username} declined your friend request.",
            content_type=content_type,                    
        )

        return receiver_notification
    
    def cancel(self):
        """
        Cancel is friend request
        It is 'cancelled' by setting the 'is_active' field to False.
        This is only different with respect to "declining" through the notification that is generated.
        """
        self.is_active = False
        self.save()

        content_type = ContentType.objects.get_for_model(self)

        # # Update notification for RECEIVER
        # receiver_notification = Notification.objects.get(target=self.receiver, content_type=content_type, object_id=self.id)

        # receiver_notification.is_active = False
        # receiver_notification.redirect_url = f"{settings.BASE_URL}/account/{self.sender.pk}/"
        # receiver_notification.verb = f"{self.sender.username} cancelled the friend request sent to you."
        # receiver_notification.timestamp = timezone.now()
        # receiver_notification.save() 

        # # Create notification for SENDER
        # self.notifications.create(
        #     target=self.sender,
        #     from_user=self.receiver,
        #     redirect_url=f"{settings.BASE_URL}/account/{self.receiver.pk}/",
        #     verb=f"You cancelled the friend request to {self.receiver.username}",
        #     content_type=content_type,                    
        # )

        # Create notification for SENDER
        self.notifications.create(
            target=self.sender,
            from_user=self.receiver,
            redirect_url=f"{settings.BASE_URL}/account/{self.receiver.pk}/",
            verb=f"You cancelled the friend request to {self.receiver.username}",
            content_type=content_type,                    
        )

        # Update notification for RECEIVER
        receiver_notification = Notification.objects.get(target=self.receiver, content_type=content_type, object_id=self.id)

        # receiver_notification.is_active = False
        receiver_notification.redirect_url = f"{settings.BASE_URL}/account/{self.sender.pk}/"
        receiver_notification.verb = f"{self.sender.username} cancelled the friend request sent to you."
        receiver_notification.read = False
        receiver_notification.save() 




    
    @property
    def get_cname(self):
        """
        For determining what kind of object is associated with a Notification
        """
        return "FriendRequest"



@receiver(post_save, sender=FriendRequest)
def create_notification(sender, instance, created, **kwargs):
    if created:
        instance.notifications.create(
            target=instance.receiver,
            from_user=instance.sender,
            redirect_url=f"{settings.BASE_URL}/account/{instance.sender.pk}/",
            verb=f"{instance.sender.username} send you a friend request.",
            content_type=instance,
        )
