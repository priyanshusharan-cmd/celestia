import physics

mu_vals = [0.001, 0.01, 0.0121, 0.0385, 0.05, 0.1, 0.3]

print(f"{'mu':<10} | {'L4':<10} | {'L5':<10} | {'L1-L3 Unstable?':<15}")
print("-" * 55)

for mu in mu_vals:
    try:
        points = physics.all_lagrange_points(mu)
        
        l4_stab = physics.stability(mu, points['L4'])['classification']
        l5_stab = physics.stability(mu, points['L5'])['classification']
        
        l1_stab = physics.stability(mu, points['L1'])['classification']
        l2_stab = physics.stability(mu, points['L2'])['classification']
        l3_stab = physics.stability(mu, points['L3'])['classification']
        
        col_unstable = all(s == 'unstable' for s in (l1_stab, l2_stab, l3_stab))
        
        print(f"{mu:<10} | {l4_stab:<10} | {l5_stab:<10} | {col_unstable!s:<15}")
    except ValueError as e:
        print(f"{mu:<10} | ERROR: {e!s}")
