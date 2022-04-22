
# lil-ink-blog

## This is a project where I built a blog using Flask

## Feature

### 1. Register


This blog allow you to register accounts using email.

You will need to provide: *email, name and password*. Password only need to pass once (Because this is a Personal Project. Might be updated in the future)

After you registered successfully. Your account will be saved into database. Your password written into database will be hash with salt. You will be **automatically logged in**

### 2. Login


After you have created your account successfully. You can use that account to login in latter time.

You need to provide your *email and password*.

### 3. Logout


You can log out of your account.

### 4. Read post


You **do not need** to login to read post.

You can tab into blog post to read it and its comment.

### 5. Comment on blog posts


You **need to login** to use this feature.

After login you can now post your comment to blog posts.

### 6. Create post


For this fearture you ***need to login as administrator (or admin-provided account)***.

As admin, you can create post.

You need to provide: *title, subtitle, body of the post (There are tools to create text), image url (which is the background image for the post)*.

### 7. Delete post


For this fearture you ***need to login as administrator***.

As admin, you can delete post By clicking on this <x> in the home page )

### 8. Edit post
  
  
For this fearture you ***need to login as administrator (or post-creator)***.

As admin (Or Post-creator) you can edit post. 

You can edit post *body, title, subtitle, image url*. **The date of post remain the same**.


