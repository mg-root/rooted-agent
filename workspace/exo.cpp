class Entity {
  private:
    double x;
    double y;
    char *name; // Added this line

  public:
    // Default constructor
    Entity() : x(0), y(0), name(nullptr) {}

    // Basic constructor that takes x and y positions
    Entity(double x, double y) : x(x), y(y), name(nullptr) {}

    // Method to set the x position
    void setX(double newX) { x = newX; }

    // Method to set the y position
    void setY(double newY) { y = newY; }
};