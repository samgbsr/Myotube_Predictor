# This file should ensure the existence of records required to run the application in every environment (production,
# development, test). The code here should be idempotent so that it can be executed at any point in every environment.
# The data can then be loaded with the bin/rails db:seed command (or created alongside the database with db:setup).
#
# Example:
#
#   ["Action", "Comedy", "Drama", "Horror"].each do |genre_name|
#     MovieGenre.find_or_create_by!(name: genre_name)
#   end
# db/seeds.rb

Project.create([
  {
    name: "Test Project 1",
    myotube_count: 10,
    picture_count: 5,
    start_date: Time.now,
    end_date: Time.now + 1.month
  },
  {
    name: "Test Project 2",
    myotube_count: 15,
    picture_count: 8,
    start_date: Time.now - 1.month,
    end_date: Time.now + 2.months
  }
])
