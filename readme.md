# Dev Log: Boids

## The Theory
Boids are an artificial life program which simulates the flocking behaviour of birds, and related group motion. They are an example of emergent behaviour: behaviour that arises from the interaction of individual agents adhering to a set of simple rules. The rules boids follow are:
- **Separation**: Steer to avoid crowing local flockmates
- **Alignment**: Steer towards the average heading of local flockmates
- **Cohesion**: Steer to move towards the average position of local flockmates

There are further rules which I may explore later, including:
- **Obstacle Detection**: Steer to avoid obstacles in the environment and the boundaries of the environment
- **Goal Seeking**: Steer towards a specified goal point

I will initially focus on the main 3 rules for boids and from there I can consider adding more complex rules.