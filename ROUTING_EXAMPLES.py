# Example of how user/member routes should be structured
# These would go in web.py or a separate users.py file

# USER PROFILE ROUTES (Dynamic - scales infinitely)
@router.get("/user/{username}/profile", response_class=HTMLResponse)
async def user_profile(request: Request, username: str, db: AsyncSession = Depends(get_db_session)):
    """Dynamic user profile - ONE route serves ALL users"""
    user = await UserService.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return templates.TemplateResponse("user_profile.html", {
        "request": request,
        "user": user,
        "clubs_owned": user.clubs_owned,
        "memberships": user.club_memberships
    })

# MEMBER ROUTES (Dynamic - scales infinitely)  
@router.get("/club/{club_slug}/member/{member_id}", response_class=HTMLResponse)
async def member_profile(request: Request, club_slug: str, member_id: str, db: AsyncSession = Depends(get_db_session)):
    """Dynamic member profile within a club - ONE route serves ALL members"""
    club = await ClubService.get_club_by_slug(db, club_slug)
    member = await MemberService.get_member_by_id(db, member_id)
    
    if not club or not member or member.club_id != club.id:
        raise HTTPException(status_code=404, detail="Member not found")
    
    return templates.TemplateResponse("member_profile.html", {
        "request": request,
        "club": club,
        "member": member,
        "bookings": member.bookings,
        "activity": member.recent_activity
    })

# CLUB OWNER DASHBOARD (Already implemented)
@router.get("/owner/{username}/dashboard", response_class=HTMLResponse) 
async def owner_dashboard(request: Request, username: str, db: AsyncSession = Depends(get_db_session)):
    """Owner dashboard showing ALL their clubs"""
    user = await UserService.get_user_by_username(db, username)
    clubs = await ClubService.get_clubs_by_owner(db, user.id)
    
    return templates.TemplateResponse("owner_dashboard.html", {
        "request": request,
        "owner": user,
        "clubs": clubs,
        "total_members": sum(club.member_count for club in clubs),
        "total_revenue": sum(club.revenue for club in clubs)
    })

# PUBLIC MEMBER DIRECTORY (Dynamic - scales infinitely)
@router.get("/club/{club_slug}/members", response_class=HTMLResponse)
async def club_members(request: Request, club_slug: str, db: AsyncSession = Depends(get_db_session)):
    """List all members of a club - ONE route serves ALL clubs"""
    club = await ClubService.get_club_by_slug(db, club_slug)
    members = await MemberService.get_club_members(db, club.id)
    
    return templates.TemplateResponse("club_members.html", {
        "request": request,
        "club": club,
        "members": members
    })