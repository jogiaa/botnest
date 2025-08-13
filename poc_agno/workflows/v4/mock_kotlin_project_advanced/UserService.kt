
package com.example.app.services

import com.example.app.models.User
import com.example.app.repositories.UserRepository

interface UserService {
    fun getUserById(id: Int): User
}
