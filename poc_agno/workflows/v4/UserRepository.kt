
package com.example.app.repositories

import com.example.app.models.User
import com.example.app.models.DatabaseConnection

class UserRepository(private val connection: DatabaseConnection , private val type:Int) {
    fun findById(id: Int): User {
        // Implementation
        return User(id, "John Doe")
    }
}
