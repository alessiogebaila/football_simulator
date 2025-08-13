#!/usr/bin/env python3
"""
🏆 TACTICAL FORMATION DEMO
Quick demonstration of tactical formation system
"""

from tactical_formations import TacticalManager, FORMATIONS

def main():
    print("🏆" + "="*60 + "🏆")
    print("  TACTICAL FORMATION SYSTEM DEMO")
    print("  Real Squad Data with Correct Formations")
    print("🏆" + "="*60 + "🏆")
    
    try:
        manager = TacticalManager('real_transfermarkt_squads.csv')
        
        print(f"\n📊 System Status:")
        print(f"  ✅ CSV loaded: {len(manager.df)} players")
        print(f"  ✅ Teams found: {manager.df['club'].nunique()}")
        print(f"  ✅ Formations defined: {len(FORMATIONS)}")
        
        print(f"\n🎯 Team Formations:")
        for team_name in sorted(FORMATIONS.keys()):
            formation = FORMATIONS[team_name]
            print(f"  {team_name:20s}: {formation.name}")
        
        # Test Barcelona squad selection
        print(f"\n🔍 Testing Barcelona (4-2-3-1) squad selection:")
        try:
            starting_xi, formation_name = manager.select_starting_xi('Barcelona')
            print(f"✅ Successfully built {formation_name} lineup!")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Test Real Madrid squad selection
        print(f"\n🔍 Testing Real Madrid (4-3-1-2) squad selection:")
        try:
            starting_xi, formation_name = manager.select_starting_xi('Real Madrid')
            print(f"✅ Successfully built {formation_name} lineup!")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print(f"\n🎮 System ready for tactical tournament simulation!")
        
    except Exception as e:
        print(f"❌ System Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
