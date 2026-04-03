"use client";
import { useState, useEffect } from "react";
import api from "./api";

/**
 * useFarm — fetches the logged-in user's farm dynamically.
 * Every page uses this instead of a hardcoded FARM_ID.
 * If the user has no farm yet, farmId will be null.
 */
export function useFarm() {
  const [farmId, setFarmId] = useState<string | null>(null);
  const [farm, setFarm] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [noFarm, setNoFarm] = useState(false);

  useEffect(() => {
    fetchFarm();
  }, []);

  const fetchFarm = async () => {
    try {
      const res = await api.get("/farms/");
      const farms = res.data.farms;
      if (farms && farms.length > 0) {
        setFarm(farms[0]);
        setFarmId(farms[0].id);
      } else {
        setNoFarm(true);
      }
    } catch {
      setNoFarm(true);
    } finally {
      setLoading(false);
    }
  };

  const refetch = () => {
    setLoading(true);
    setNoFarm(false);
    fetchFarm();
  };

  return { farmId, farm, loading, noFarm, refetch };
}
