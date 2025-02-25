"use client";
import React from "react";
import { motion } from "framer-motion";

export default function ColourfulText({ text }: { text: string }) {
  const colors = [
    "rgb(255, 103, 31)",   // NPCI Bright Orange
    "rgb(255, 165, 0)",    // Vibrant Orange
    "rgb(255, 183, 77)",   // Luminous Amber
    "rgb(0, 208, 76)",     // Electric Green
    "rgb(0, 200, 83)",     // Bright NPCI Green
    "rgb(46, 255, 123)",   // Neon Green
    "rgb(0, 123, 255)",    // Vivid Blue
    "rgb(51, 153, 255)",   // Bright Sky Blue
    "rgb(80, 120, 255)",   // Electric Blue
    "rgb(116, 141, 255)"   // Bright Periwinkle
  ];
  const [currentColors, setCurrentColors] = React.useState(colors);
  const [count, setCount] = React.useState(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      const shuffled = [...colors].sort(() => Math.random() - 0.5);
      setCurrentColors(shuffled);
      setCount((prev) => prev + 1);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return text.split("").map((char, index) => (
    <motion.span
      key={`${char}-${count}-${index}`}
      initial={{
        y: 0,
      }}
      animate={{
        color: currentColors[index % currentColors.length],
        y: [0, -3, 0],
        scale: [1, 1.01, 1],
        filter: ["blur(0px)", `blur(5px)`, "blur(0px)"],
        opacity: [1, 0.8, 1],
      }}
      transition={{
        duration: 0.5,
        delay: index * 0.05,
      }}
      className="inline-block whitespace-pre font-sans tracking-tight"
    >
      {char}
    </motion.span>
  ));
}
