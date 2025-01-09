from instorage.securitylevels.api.security_level_models import SecurityLevelPublic
from instorage.securitylevels.security_level import SecurityLevel
from instorage.users.user import UserInDB


class SecurityLevelAssembler:
    def __init__(self, user: UserInDB):
        self.user = user

    def from_security_level_to_model(self, security_level: SecurityLevel) -> SecurityLevelPublic:
        return SecurityLevelPublic(
            created_at=security_level.created_at,
            updated_at=security_level.updated_at,
            id=security_level.id,
            name=security_level.name,
            description=security_level.description,
            value=security_level.value,
            tenant_id=security_level.tenant_id,
        )
