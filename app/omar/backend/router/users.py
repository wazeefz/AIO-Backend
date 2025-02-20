from . import database, schemas 
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.db_connection import get_db

router = APIRouter()

@router.post("/signup/")
async def signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Check if email already exists
    print("checkpoint1")
    existing_user = db.query(User).filter(User.email == user.email).first()
    print("checkpoint2")
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create new user
    try:
        # Hash the password
        hashed_password = pwd_context.hash(user.password)
        
        # Create new user object
        db_user = User(
            name=user.name,
            email=user.email,
            password=hashed_password,
            department_id=user.department_id,
            role=user.role
        )
        
        # Add to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return {"message": "User created successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating user: {str(e)}"
        )

@router.post("/login/", response_model=schemas.Token)
async def login(login_request: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    # Find user by email
    user = db.query(User).filter(User.email == login_request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(login_request.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.user_id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.name
    }

@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(database.get_db)
):
    # Find the user in the database
    db_user = db.query(User).filter(User.user_id == user_id).first()
    
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Check if email is being updated and if it's already taken
    if user_update.email and user_update.email != db_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
    
    try:
        # Update user fields if they are provided
        if user_update.name is not None:
            db_user.name = user_update.name
        
        if user_update.email is not None:
            db_user.email = user_update.email
            
        if user_update.password is not None:
            db_user.password = pwd_context.hash(user_update.password)
            
        if user_update.department_id is not None:
            # Optionally verify that the department exists
            # department = db.query(Department).filter(
            #     Department.department_id == user_update.department_id
            # ).first()
            # if not department:
            #     raise HTTPException(
            #         status_code=404,
            #         detail="Department not found"
            #     )
            db_user.department_id = user_update.department_id
            
        if user_update.role is not None:
            db_user.role = user_update.role
        
        # Commit the changes to the database
        db.commit()
        db.refresh(db_user)
        
        # Return the updated user information
        return {
            "message": "User updated successfully",
            "user": {
                "user_id": db_user.user_id,
                "name": db_user.name,
                "email": db_user.email,
                "department_id": db_user.department_id,
                "role": db_user.role
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating user: {str(e)}"
        )
    
@router.get("/users/", response_model=List[schemas.UserResponse])
async def get_users(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving users: {str(e)}"
        )

# Get specific user by ID endpoint
@router.get("/users/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: Session = Depends(database.get_db)):
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        print("checkpoint4")
        return user
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user: {str(e)}"
        )
    

# Ask Question Endpoint
@router.get("/ask-question/")
async def ask_question(
    question: str = Query(..., description="Your question"),
    pdf_file: str = Query(None, description="Optional: Specific PDF to search in")
):
    try:
        search_kwargs = {}
        if pdf_file:
            search_kwargs = {
                "filter": {"metadata.source_file": pdf_file}
            }
        
        retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
        
        chain = RetrievalQA.from_chain_type(
            llm=llm_model,
            retriever=retriever,
            chain_type="stuff",
            return_source_documents=True
        )
        
        result = chain.invoke(question)
        
        sources = []
        if hasattr(result, 'get') and result.get('source_documents'):
            for doc in result['source_documents']:
                if 'source_file' in doc.metadata and doc.metadata['source_file'] not in sources:
                    sources.append(doc.metadata['source_file'])
        
        return {
            "question": question,
            "answer": result["result"],
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")