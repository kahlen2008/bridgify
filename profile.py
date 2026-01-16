class Profile:
    def __init__(self,user_id,password,first_name,last_name,display_name,profile_picture,email,user_type,role):
        self.__user_id = user_id
        self.__password = password
        self.__first_name = first_name
        self.__last_name = last_name
        self.__display_name = display_name
        self.__email = email
        self.__profile_picture = profile_picture
        self.__user_type = user_type
        self.__role = role

    def get_user_id(self):
        return self.__user_id
    
    def get_password(self):
        return self.__password

    def get_first_name(self):
        return self.__first_name
    
    def get_last_name(self):
        return self.__last_name
    
    def get_full_name(self):
        return f"{self.__first_name} {self.__last_name}"
    
    def get_display_name(self):
        return self.__display_name
    
    def get_email(self):
        return self.__email
    
    def get_profile_picture(self):
        return self.__profile_picture
    
    def get_user_type(self):
        return self.__user_type
    
    def get_role(self):
        return self.__role
    
    def set_user_id(self, user_id):
        self.__user_id = user_id

    def set_password(self, password):
        self.__password = password
    
    def set_first_name(self,first_name):
        self.__first_name = first_name

    def set_last_name(self,last_name):
        self.__last_name = last_name

    def set_display_name(self,display_name):
        self.__display_name = display_name

    def set_email(self,email):
        self.__email = email

    def set_profile_picture(self,profile_picture):
        self.__profile_picture = profile_picture

    def set_user_type(self,user_type):
        self.__user_type = user_type

    def set_role(self,role):
        self.__role = role

    @classmethod
    def from_database_row(cls, row_data):
        return cls(
            user_id=row_data[0],
            password=row_data[1], 
            first_name=row_data[2],
            last_name=row_data[3],
            display_name=row_data[4],
            email=row_data[5],
            profile_picture=row_data[6],
            user_type=row_data[7],
            role=row_data[8]
        ) 