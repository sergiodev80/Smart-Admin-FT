import logging

logger = logging.getLogger(__name__)


class ERPUserService:
    """
    Stub for ERP integration. Replace with real implementation per project.
    """

    @staticmethod
    def find_by_email(email: str):
        """
        Look up a user in the external ERP by email.
        Return a dict with at least {"name": str, "login": str} or None if not found.
        """
        logger.warning(
            "ERPUserService.find_by_email called but no ERP integration configured. "
            "Replace apps/erp_sync/services.py with real implementation."
        )
        return None
