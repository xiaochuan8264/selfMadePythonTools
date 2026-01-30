# 如何查询所有用户，建立了session之后

def list_all_users():
    """列出系统中所有用户"""
    users = session.query('User').all()
    
    print("系统中的所有用户:")
    for user in users:
        print(f"  用户名: {user['username']}, 邮箱: {user['email']}, ID: {user['id']}")
    
    return users

# 使用
list_all_users()