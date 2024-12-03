class Myotube < ApplicationRecord
  belongs_to :image

  validates :height, :width, :x_center, :y_center, :rotation, :confidence, :type_class, presence: true
  validates :confidence, numericality: { greater_than_or_equal_to: 0, less_than_or_equal_to: 1 }
end
