import copy
import datetime
from unittest import mock

import pytest

from ami.followup.data.notification import get_notifications_data, get_notifications_source
from ami.followup.schemas import (
    FollowupItem,
    FollowupItemEvent,
    FollowupSource,
    FollowupSourceStatus,
    FollowupSubItem,
    ItemGenericStatus,
)
from ami.notification.models import Notification
from ami.partner.models import partners
from ami.service.models import Service
from ami.user.models import User


@pytest.mark.django_db
def test_get_notifications_data_no_notifications_for_user(user: User) -> None:
    other_user = User.objects.create(fc_hash="fc-hash")
    Notification.objects.create(  # Other notification
        user_id=other_user.id,
        content_body="Other notification",
        content_title="Notification title",
        partner_id="psl",
    )

    result = get_notifications_data(current_user=user)

    assert result == []


@pytest.mark.django_db
def test_get_notifications_data_partner_without_notifications(
    user: User, monkeypatch: pytest.MonkeyPatch
) -> None:
    partner = copy.deepcopy(partners["psl"])
    partner.followup_from_notifications = False
    monkeypatch.setattr("ami.followup.data.notification.partners", {"psl": partner})
    Notification.objects.create(  # Other notification
        user_id=user.id,
        content_body="Other notification",
        content_title="Notification title",
        partner_id="psl",
    )

    result = get_notifications_data(current_user=user)

    assert result == []


@pytest.mark.django_db
def test_get_notifications_data_incomplete_notifications(user: User) -> None:
    # no item_generic_status
    Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        partner_id="psl",
    )
    # no item_status_label
    Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        partner_id="psl",
    )
    # no item_type
    Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_id="42",
        partner_id="psl",
    )
    # no item_id
    Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        partner_id="psl",
    )

    result = get_notifications_data(current_user=user)

    assert result == []


@pytest.mark.django_db
def test_get_notifications_data_invalid_notifications(user: User) -> None:
    # invalid item_generic_status
    Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="invalid",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        partner_id="psl",
    )

    result = get_notifications_data(current_user=user)

    assert result == []


@pytest.mark.django_db
def test_get_notifications_data(user: User, monkeypatch: pytest.MonkeyPatch) -> None:
    Service.objects.create(
        partner_id="psl",
        item_type="OperationTranquilliteVacances",
        title="Opération Tranquillité Vacances",
        short_description="Inscrivez-vous pour protéger votre domicile pendant votre absence",
        description="Pendant toute absence prolongée de votre domicile, vous pouvez vous inscrire à l'**opération tranquillité vacances**.",
        url="https://localhost:8000/mademarche/demarcheGenerique/?codeDemarche=OperationTranquilliteVacances&caller={back_param_token_jwt}",
        with_silent_login=True,
    )

    notification1 = Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_private_body="with private body",
        content_title="Notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        partner_id="psl",
    )
    notification2 = Notification.objects.create(
        user_id=user.id,
        content_body="notification 2",
        content_title="Notification title 2",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        item_is_archived=True,
        partner_id="psl",
    )
    notification3 = Notification.objects.create(
        user_id=user.id,
        content_body="notification 3",
        content_title="Notification title 3",
        item_generic_status="wip",
        item_status_label="En cours",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        partner_id="psl",
    )
    sub_notification31 = Notification.objects.create(
        user_id=user.id,
        content_body="Sub notification body",
        content_title="Sub notification title",
        content_subheading="Autre service",
        item_generic_status="wip",
        item_status_label="En cours",
        item_type="SousDémarche",
        item_id="35",
        partner_id="dinum-ami",
        item_parent_partner_id="psl",
        item_parent_type="OperationTranquilliteVacances",
        item_parent_id="42",
    )

    notification4 = Notification.objects.create(
        user_id=user.id,
        content_body="notification 4",
        content_title="Notification title 4",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OtherOperationTranquilliteVacances",
        item_id="43",
        content_link="http://foo.com",
        item_is_archived=False,
        partner_id="psl",
    )

    notification5 = Notification.objects.create(
        user_id=user.id,
        content_body="notification 5",
        content_title="Notification title 5",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="44",
        content_link="http://bar.com",
        item_is_archived=True,
        partner_id="psl",
    )
    notification6 = Notification.objects.create(
        user_id=user.id,
        content_body="notification 6",
        content_title="Notification title 6",
        item_generic_status="closed",
        item_status_label="Validé",
        item_type="OperationTranquilliteVacances",
        item_id="44",
        item_milestone_start_date=datetime.datetime.now(datetime.timezone.utc),
        item_milestone_end_date=datetime.datetime.now(datetime.timezone.utc),
        item_is_archived=False,
        partner_id="psl",
    )

    notification7 = Notification.objects.create(
        user_id=user.id,
        content_body="other notification",
        content_title="Other Notification title",
        item_generic_status="closed",
        item_status_label="Validé",
        item_type="Other",
        item_id="42",
        partner_id="dinum-ami",
    )

    notification8 = Notification.objects.create(
        user_id=user.id,
        content_body="other notification",
        content_private_body="some private body content",
        content_subheading="content subheading",
        content_title="Other Notification title",
        content_icon="dinum-ami-icon",
        item_generic_status="closed",
        item_status_label="Validé",
        item_type="Other",
        item_id="52",
        partner_id="dinum-ami",
    )

    result = get_notifications_data(current_user=user)

    assert result == [
        FollowupItem(
            partner_id="dinum-ami",
            item_type="Other",
            item_external_id="52",
            status_id=ItemGenericStatus.CLOSED,
            status_label="Validé",
            milestone_start_date=None,
            milestone_end_date=None,
            events=[
                FollowupItemEvent(
                    notification8.id,
                    notification8.created_at,
                    "other notification\n\nsome private body content",
                ),
            ],
            title="Other Notification title",
            subheading="content subheading",
            description="other notification\n\nsome private body content",
            icon="dinum-ami-icon",
            external_url=None,
            is_archived=False,
            created_at=notification8.event_date,
            updated_at=notification8.event_date,
            sub_items=[],
        ),
        FollowupItem(
            partner_id="dinum-ami",
            item_type="Other",
            item_external_id="42",
            status_id=ItemGenericStatus.CLOSED,
            status_label="Validé",
            milestone_start_date=None,
            milestone_end_date=None,
            events=[
                FollowupItemEvent(
                    notification7.id,
                    notification7.created_at,
                    "other notification",
                ),
            ],
            title="Other Notification title",
            subheading="AMI",
            description="other notification",
            icon="fr-icon-flag-fill",
            external_url=None,
            is_archived=False,
            created_at=notification7.event_date,
            updated_at=notification7.event_date,
            sub_items=[],
        ),
        FollowupItem(
            partner_id="psl",
            item_type="OperationTranquilliteVacances",
            item_external_id="44",
            status_id=ItemGenericStatus.CLOSED,
            status_label="Validé",
            milestone_start_date=notification6.item_milestone_start_date,
            milestone_end_date=notification6.item_milestone_end_date,
            events=[
                FollowupItemEvent(
                    notification5.id,
                    notification5.created_at,
                    "notification 5",
                ),
                FollowupItemEvent(
                    notification6.id,
                    notification6.created_at,
                    "notification 6",
                ),
            ],
            title="Opération Tranquillité Vacances",
            subheading="PSL",
            description="notification 6",
            icon="fr-icon-flag-fill",
            external_url="http://bar.com",
            is_archived=False,
            created_at=notification5.event_date,
            updated_at=notification6.event_date,
            sub_items=[],
        ),
        FollowupItem(
            partner_id="psl",
            item_type="OtherOperationTranquilliteVacances",
            item_external_id="43",
            status_id=ItemGenericStatus.NEW,
            status_label="Nouveau",
            milestone_start_date=None,
            milestone_end_date=None,
            events=[
                FollowupItemEvent(
                    notification4.id,
                    notification4.created_at,
                    "notification 4",
                ),
            ],
            title="Notification title 4",
            subheading="PSL",
            description="notification 4",
            icon="fr-icon-mail-fill",
            external_url="http://foo.com",
            is_archived=False,
            created_at=notification4.event_date,
            updated_at=notification4.event_date,
            sub_items=[],
        ),
        FollowupItem(
            partner_id="psl",
            item_type="OperationTranquilliteVacances",
            item_external_id="42",
            status_id=ItemGenericStatus.WIP,
            status_label="En cours",
            milestone_start_date=None,
            milestone_end_date=None,
            events=[
                FollowupItemEvent(
                    notification1.id,
                    notification1.created_at,
                    "notification 1\n\nwith private body",
                ),
                FollowupItemEvent(
                    notification2.id,
                    notification2.created_at,
                    "notification 2",
                ),
                FollowupItemEvent(
                    notification3.id,
                    notification3.created_at,
                    "notification 3",
                ),
            ],
            title="Opération Tranquillité Vacances",
            subheading="PSL",
            description="notification 3",
            icon="fr-icon-eye-fill",
            external_url=None,
            is_archived=True,
            created_at=notification1.event_date,
            updated_at=notification3.event_date,
            sub_items=[
                FollowupSubItem(
                    partner_id="dinum-ami",
                    item_type="SousDémarche",
                    item_external_id="35",
                    status_id=ItemGenericStatus.WIP,
                    status_label="En cours",
                    milestone_start_date=None,
                    milestone_end_date=None,
                    events=[
                        FollowupItemEvent(
                            sub_notification31.id,
                            sub_notification31.created_at,
                            "Sub notification body",
                        ),
                    ],
                    title="Sub notification title",
                    subheading="Autre service",
                    description="Sub notification body",
                    icon="fr-icon-eye-fill",
                    external_url=None,
                    is_archived=False,
                    created_at=sub_notification31.event_date,
                    updated_at=sub_notification31.event_date,
                ),
            ],
        ),
    ]


@pytest.mark.django_db
def test_get_notifications_data_parent_and_sub_items(
    user: User, monkeypatch: pytest.MonkeyPatch
) -> None:
    notification = Notification.objects.create(
        user_id=user.id,
        content_body="notification",
        content_title="Notification title",
        item_generic_status="wip",
        item_status_label="En cours",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        partner_id="psl",
    )
    sub_notification1 = Notification.objects.create(
        user_id=user.id,
        content_body="Sub notification body 1",
        content_title="Sub notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="SousDémarche",
        item_id="35",
        partner_id="dinum-ami",
        item_parent_partner_id="psl",
        item_parent_type="OperationTranquilliteVacances",
        item_parent_id="42",
    )
    sub_notification2 = Notification.objects.create(
        user_id=user.id,
        content_body="Sub notification body 2",
        content_title="Sub notification title 2",
        item_generic_status="wip",
        item_status_label="En cours",
        item_type="SousDémarche",
        item_id="35",
        partner_id="dinum-ami",
        item_parent_partner_id="psl",
        item_parent_type="OperationTranquilliteVacances",
        item_parent_id="42",
    )
    sub_notification3 = Notification.objects.create(
        user_id=user.id,
        content_body="Sub notification body 3",
        content_title="Sub notification title 3",
        content_subheading="Autre service",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="SousDémarcheBis",
        item_id="104",
        partner_id="dinum-ami",
        item_parent_partner_id="psl",
        item_parent_type="OperationTranquilliteVacances",
        item_parent_id="42",
    )

    result = get_notifications_data(current_user=user)

    assert result == [
        FollowupItem(
            partner_id="psl",
            item_type="OperationTranquilliteVacances",
            item_external_id="42",
            status_id=ItemGenericStatus.WIP,
            status_label="En cours",
            milestone_start_date=None,
            milestone_end_date=None,
            events=[
                FollowupItemEvent(
                    id=notification.id,
                    created_at=notification.created_at,
                    description="notification",
                )
            ],
            title="Notification title",
            subheading="PSL",
            description="notification",
            icon="fr-icon-eye-fill",
            external_url=None,
            is_archived=False,
            created_at=notification.event_date,
            updated_at=notification.event_date,
            sub_items=[
                FollowupSubItem(
                    partner_id="dinum-ami",
                    item_type="SousDémarcheBis",
                    item_external_id="104",
                    status_id=ItemGenericStatus.NEW,
                    status_label="Nouveau",
                    milestone_start_date=None,
                    milestone_end_date=None,
                    events=[
                        FollowupItemEvent(
                            id=sub_notification3.id,
                            created_at=sub_notification3.created_at,
                            description="Sub notification body 3",
                        )
                    ],
                    title="Sub notification title 3",
                    subheading="Autre service",
                    description="Sub notification body 3",
                    icon="fr-icon-mail-fill",
                    external_url=None,
                    is_archived=False,
                    created_at=sub_notification3.event_date,
                    updated_at=sub_notification3.event_date,
                ),
                FollowupSubItem(
                    partner_id="dinum-ami",
                    item_type="SousDémarche",
                    item_external_id="35",
                    status_id=ItemGenericStatus.WIP,
                    status_label="En cours",
                    milestone_start_date=None,
                    milestone_end_date=None,
                    events=[
                        FollowupItemEvent(
                            id=sub_notification1.id,
                            created_at=sub_notification1.created_at,
                            description="Sub notification body 1",
                        ),
                        FollowupItemEvent(
                            id=sub_notification2.id,
                            created_at=sub_notification2.created_at,
                            description="Sub notification body 2",
                        ),
                    ],
                    title="Sub notification title 2",
                    subheading="AMI",
                    description="Sub notification body 2",
                    icon="fr-icon-eye-fill",
                    external_url=None,
                    is_archived=False,
                    created_at=sub_notification1.event_date,
                    updated_at=sub_notification2.event_date,
                ),
            ],
        ),
    ]


@pytest.mark.django_db
def test_get_notifications_data_parent_and_sub_sub_items(
    user: User, monkeypatch: pytest.MonkeyPatch
) -> None:
    notification = Notification.objects.create(
        user_id=user.id,
        content_body="notification",
        content_title="Notification title",
        item_generic_status="wip",
        item_status_label="En cours",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        partner_id="psl",
    )
    sub_notification = Notification.objects.create(
        user_id=user.id,
        content_body="Sub notification body",
        content_title="Sub notification title",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="SousDémarche",
        item_id="35",
        partner_id="dinum-ami",
        item_parent_partner_id="psl",
        item_parent_type="OperationTranquilliteVacances",
        item_parent_id="42",
    )
    sub_sub_notification = Notification.objects.create(
        user_id=user.id,
        content_body="Sub sub notification body",
        content_title="Sub sub notification title",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="SousSousDémarche",
        item_id="350",
        partner_id="dinum-dn",
        item_parent_partner_id="dinum-ami",
        item_parent_type="SousDémarche",
        item_parent_id="35",
    )

    result = get_notifications_data(current_user=user)

    # sub_notification is parent AND child
    assert result == [
        FollowupItem(
            partner_id="dinum-ami",
            item_type="SousDémarche",
            item_external_id="35",
            status_id=ItemGenericStatus.NEW,
            status_label="Nouveau",
            milestone_start_date=None,
            milestone_end_date=None,
            events=[
                FollowupItemEvent(
                    id=sub_notification.id,
                    created_at=sub_notification.created_at,
                    description="Sub notification body",
                )
            ],
            title="Sub notification title",
            subheading="AMI",
            description="Sub notification body",
            icon="fr-icon-mail-fill",
            external_url=None,
            is_archived=False,
            created_at=sub_notification.event_date,
            updated_at=sub_notification.event_date,
            sub_items=[
                FollowupSubItem(
                    partner_id="dinum-dn",
                    item_type="SousSousDémarche",
                    item_external_id="350",
                    status_id=ItemGenericStatus.NEW,
                    status_label="Nouveau",
                    milestone_start_date=None,
                    milestone_end_date=None,
                    events=[
                        FollowupItemEvent(
                            id=sub_sub_notification.id,
                            created_at=sub_sub_notification.created_at,
                            description="Sub sub notification body",
                        )
                    ],
                    title="Sub sub notification title",
                    subheading="demarche.numerique.gouv.fr",
                    description="Sub sub notification body",
                    icon="fr-icon-mail-fill",
                    external_url=None,
                    is_archived=False,
                    created_at=sub_sub_notification.event_date,
                    updated_at=sub_sub_notification.event_date,
                )
            ],
        ),
        FollowupItem(
            partner_id="psl",
            item_type="OperationTranquilliteVacances",
            item_external_id="42",
            status_id=ItemGenericStatus.WIP,
            status_label="En cours",
            milestone_start_date=None,
            milestone_end_date=None,
            events=[
                FollowupItemEvent(
                    id=notification.id,
                    created_at=notification.created_at,
                    description="notification",
                )
            ],
            title="Notification title",
            subheading="PSL",
            description="notification",
            icon="fr-icon-eye-fill",
            external_url=None,
            is_archived=False,
            created_at=notification.event_date,
            updated_at=notification.event_date,
            sub_items=[
                FollowupSubItem(
                    partner_id="dinum-ami",
                    item_type="SousDémarche",
                    item_external_id="35",
                    status_id=ItemGenericStatus.NEW,
                    status_label="Nouveau",
                    milestone_start_date=None,
                    milestone_end_date=None,
                    events=[
                        FollowupItemEvent(
                            id=sub_notification.id,
                            created_at=sub_notification.created_at,
                            description="Sub notification body",
                        )
                    ],
                    title="Sub notification title",
                    subheading="AMI",
                    description="Sub notification body",
                    icon="fr-icon-mail-fill",
                    external_url=None,
                    is_archived=False,
                    created_at=sub_notification.event_date,
                    updated_at=sub_notification.event_date,
                )
            ],
        ),
    ]


@pytest.mark.django_db
def test_get_notifications_source(user: User, monkeypatch: pytest.MonkeyPatch) -> None:
    items = [
        FollowupItem(
            partner_id="psl",
            item_type="OperationTranquilliteVacances",
            item_external_id="44",
            status_id=ItemGenericStatus.CLOSED,
            status_label="Validé",
            milestone_start_date=datetime.datetime.now(datetime.timezone.utc),
            milestone_end_date=datetime.datetime.now(datetime.timezone.utc),
            events=[],
            title="Notification title 6",
            subheading="PSL",
            description="notification 6",
            icon="",
            external_url="http://bar.com",
            is_archived=False,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
            sub_items=[],
        ),
        FollowupItem(
            partner_id="psl",
            item_type="OperationTranquilliteVacances",
            item_external_id="43",
            status_id=ItemGenericStatus.NEW,
            status_label="Nouveau",
            milestone_start_date=None,
            milestone_end_date=None,
            events=[],
            title="Notification title 4",
            subheading="PSL",
            description="notification 4",
            icon="",
            external_url="http://foo.com",
            is_archived=False,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
            sub_items=[],
        ),
    ]
    data_mock = mock.Mock(return_value=items)
    monkeypatch.setattr("ami.followup.data.notification.get_notifications_data", data_mock)
    result = get_notifications_source(current_user=user)
    assert result == FollowupSource(status=FollowupSourceStatus.SUCCESS, items=items)
