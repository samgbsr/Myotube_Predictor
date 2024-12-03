class Project < ApplicationRecord
    has_many :images, dependent: :destroy
  
    validates :name, presence: true, length: { maximum: 100 }
    validates :myotube_count, :picture_count, numericality: { only_integer: true, greater_than_or_equal_to: 0 }
  end
  