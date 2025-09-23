from fastapi import APIRouter

# Create router for API endpoints
router = APIRouter(prefix="/api/v1", tags=["api"])

@router.get("/health")
async def health_check():
    """API health check"""
    return {"status": "healthy", "service": "ClubLaunch API"}

@router.get("/clubs")
async def get_clubs():
    """Get all clubs"""
    return {"message": "Clubs endpoint - coming soon"}

@router.get("/users")
async def get_users():
    """Get all platform users"""
    return {"message": "Users endpoint - coming soon"}
