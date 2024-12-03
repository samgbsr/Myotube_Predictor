class Image < ApplicationRecord
  belongs_to :project
  has_many :myotubes, dependent: :destroy

  validates :file_name, presence: true
  validates :myotube_amount, numericality: { only_integer: true, greater_than_or_equal_to: 0 }
end
