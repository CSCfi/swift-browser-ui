"""Locust file for testing the backend API performace."""

from locust import HttpLocust, TaskSet


def login(l_instance):
    """Handle locust user login."""
    l_instance.client.post(
        "/login/websso",
        {"token": "the_actual_token_doesn't_matter"}
    )


def logout(l_instance):
    """Handle locust user logout."""
    l_instance.client.get(
        "/login/kill"
    )


def api_containers(l_instance):
    """Get container listing."""
    l_instance.client.get(
        "/api/buckets"
    )


def api_objects(l_instance):
    """Get object listing."""
    l_instance.client.get(
        "/api/objects?bucket=test-container-0"
    )


def api_active(l_instance):
    """Get active project."""
    l_instance.client.get(
        "/api/active"
    )


def api_projects(l_instance):
    """Get available projects."""
    l_instance.client.get(
        "/api/projects"
    )


def api_username(l_instance):
    """Get the username."""
    l_instance.client.get(
        "/api/username"
    )


def api_project_meta(l_instance):
    """Get the project metadata."""
    l_instance.client.get(
        "/api/get-project-meta"
    )


class UserBehaviour(TaskSet):
    """Locust task class for swift-browser-ui user case."""

    tasks = {
        api_containers: 1,
        api_objects: 5,
        api_active: 1,
        api_projects: 1,
        api_username: 1,
        api_project_meta: 2,
    }

    def on_start(self):
        """Handle website login."""
        login(self)

    def on_stop(self):
        """Handle website logout."""
        logout(self)


class APIUser(HttpLocust):
    """Locust API user class."""

    task_set = UserBehaviour
    min_wait = 100
    max_wait = 1000
